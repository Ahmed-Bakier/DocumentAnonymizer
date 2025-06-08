import os
import re
import fitz  # PyMuPDF
import spacy

from django.shortcuts import get_object_or_404
from django.core.files.base import ContentFile
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import FileResponse, HttpResponseNotFound
from ..models import Article, Log, Reviewer
from .classification_config import CATEGORIES  

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTLine, LAParams

from ..models import Article, Log
from ..serializers import ArticleSerializer, LogRecordSerializer
from collections import defaultdict
from ..utils import encryption
import json
from django.conf import settings









EMAIL_REGEX = r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"

class ArticleListView(generics.ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer


NAME_REGEX = r"\b([A-Z][a-z]+(?: [A-Z][a-z]+){1,2})\b"


# Tek isim veya iki isim (ör. "Anubhav", "Diksha Kalra")
SIMPLE_NAME_REGEX = re.compile(r"^[A-Z][a-z]+(?: [A-Z][a-z]+)?$")


# Gelişmiş bir İngilizce Transformer tabanlı model (PERSON tespiti daha iyi)
nlp = spacy.load("en_core_web_trf")

def category_mapping(key):
    return {
        "name": "name",
        "contact": "contact",
        "affiliation": "affiliation"
    }.get(key, key)


def is_possible_name(text):
    """
    Spacy PERSON etiketlemese bile,
    1-3 kelimelik ve her kelimesi büyük harfle başlıyorsa
    (veya 'S.' gibi kısaltma içeriyorsa) 'isim' olabileceğini varsayıyoruz.
    Örn:
      - 'Anubhav'
      - 'S. Indu'
      - 'Divyashikha Sethia'
    """
    tokens = text.split()
    if not 1 <= len(tokens) <= 3:
        return False

    for t in tokens:
        # 'S.' veya 'S' veya 'Indu' gibi desenlere izin veriyoruz
        # İlk harf büyük, devamı küçük ya da nokta olabilir
        # Örnek regex: ^[A-Z][a-z]*\.?$
        if not re.match(r'^[A-Z][a-zA-Z]*\.?$', t.strip()):
            return False
    return True



def is_consecutive_uppercase(s):
    """
    Türkçe karakterler (Ç,Ğ,İ,Ö,Ş,Ü) dahil A-Z harflerini
    kapsayacak şekilde regex yazıyoruz.
    En az 2 karakter olsun ki tek harfli "A" vb. kısaltmalar takılmasın.
    """
    return bool(re.match(r'^[A-ZÇĞİÖŞÜ]{2,}$', s))

class AnonymizeArticleView(APIView):
    """
    Kullanıcının seçtiği (yazar adı-soyadı, e-posta, kurum) seçeneklerine göre
    sadece ilgili alanları anonimleştiren API.
    """

    def post(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)
        if not article.pdf_file:
            return Response({"error": "PDF file not found."}, status=status.HTTP_400_BAD_REQUEST)

        anonymize_options = request.data.get("anonymize_options", {})
        pdf_path = article.pdf_file.path

        anonymized_pdf_path, collected_data = self.anonymize_pdf_words(pdf_path, anonymize_options)

        # PDF'yi kaydet
        with open(anonymized_pdf_path, "rb") as f:
            article.anonymized_pdf_file.save(
                f"anonymized_{article.tracking_number}.pdf",
                ContentFile(f.read())
            )

        # Şifrelenmiş verileri JSON'a kaydet
        encrypted_data = {"name": [], "contact": [], "affiliation": []}
        for category in ["name", "contact", "affiliation"]:
            if anonymize_options.get(category_mapping(category)) and category in collected_data:
                for item in collected_data[category]:
                    enc = encryption.encrypt_data(item["text"], settings.FERNET_KEY).decode()
                    encrypted_data[category].append({
                        "encrypted": enc,
                        "page": item["page"],
                        "bbox": item["bbox"],
                        "font": item.get("font", "helv"),
                        "size": item.get("size", 10)
                    })

        json_path = os.path.join("media/anonymized_articles", f"{article.tracking_number}_enc.json")
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(encrypted_data, f, ensure_ascii=False, indent=2)

        article.encrypted_metadata_path = json_path
        article.status = "anonymized"
        article.save()
        Log.objects.create(article=article, description="Makale anonimleştirildi ve şifreli veriler kaydedildi.")

        return Response({
            "message": "Makale başarıyla anonimleştirildi!",
            "file": article.anonymized_pdf_file.url
        })

    def anonymize_pdf_words(self, pdf_path, anonymize_options):
        """
        1) İlk 2 sayfada, 'abstract'/'introduction' görünene kadar spacy + regex ile yazar bilgilerini tespit eder.
           Aynı satırda hem PERSON hem ORG (kurum) varsa ikisini de yakalar.
        2) Seçilen kategori(ler) için kelime bazında maskeleme yapar.
        """
        output_pdf_path = pdf_path.replace(".pdf", "_anonymized.pdf")
        doc = fitz.open(pdf_path)

        emails_set = set()
        persons_set = set()
        orgs_set = set()
        found_author_end = False

        collected_data = {"name": [], "contact": [], "affiliation": []}

        # 1) Tespit (ilk 2 sayfa)
        for page_index, page in enumerate(doc[:2]):
            if found_author_end:
                break

            blocks = page.get_text("blocks")
            for b in blocks:
                block_text = b[4].strip()
                if not block_text:
                    continue

                # 'abstract' veya 'introduction' görürsek dur
                if re.search(r'\b(abstract|introduction)\b', block_text.lower()):
                    found_author_end = True
                    print(f"[INFO] Found termination block: {block_text}")
                    break

                # Satır bazında inceleme
                lines = [line.strip() for line in block_text.splitlines() if line.strip()]
                for line in lines:
                    # 1A) E-posta (regex)
                    found_emails = re.findall(EMAIL_REGEX, line)
                    for em in found_emails:
                        em_lower = em.lower()
                        if em_lower not in emails_set:
                            emails_set.add(em_lower)
                            
                            print(f"[INFO] Found email='{em_lower}' (page={page_index})")

                    # 1B) Spacy ent analizi
                    doc_line = nlp(line)
                    # Bir satırda birden fazla ent olabilir (ör. hem PERSON hem ORG)
                    found_ent = False
                    for ent in doc_line.ents:
                        ent_text = ent.text.strip()
                        ent_lower = ent_text.lower()

                        if ent.label_ == "PERSON":
                            if ent_lower not in persons_set:
                                persons_set.add(ent_lower)
                                
                                print(f"[INFO] Found PERSON: {ent_text} (page={page_index})")
                            found_ent = True

                        elif ent.label_ in ["ORG", "GPE", "LOC"]:
                            if ent_lower not in orgs_set:
                                orgs_set.add(ent_lower)
                                
                                print(f"[INFO] Found ORG/GPE/LOC: {ent_text} (page={page_index})")
                            found_ent = True

                    # 1C) Fallback: Spacy hiçbir ent bulamadıysa ama satır isme benziyorsa
                    '''if not found_emails and not found_ent:
                        # e‑posta yok, spacy ent yok → belki "is_possible_name"
                        if is_possible_name(line):
                            lower_name = line.lower()
                            if lower_name not in persons_set:
                                persons_set.add(lower_name)
                                collected_data["name"].append({
                                    "text": lower_name,
                                    "page": page_index,
                                    "bbox": [b[0], b[1], b[2], b[3]],
                                    "font": "helv",
                                    "size": 10
                                })
                                print(f"[FALLBACK] Found name: {line} (page={page_index})")'''

            if found_author_end:
                break

        # 2) Maskeleme (kelime bazında)
        def word_in_set(word, full_set):
            # Eğer word, set içindeki ifadelerin tokenlarından biriyse True
            for phrase in full_set:
                tokens = phrase.split()
                if word in tokens:
                    return True
            return False

        for page_index, page in enumerate(doc):
            words = page.get_text("words", flags=1)
            for w_item in words:
                if len(w_item) < 8:
                    continue

                x0, y0, x1, y1, text, block_no, line_no, word_no = w_item[:8]
                font = w_item[8] if len(w_item) > 8 else "helv"
                size = w_item[9] if len(w_item) > 9 else 10

                text_stripped = text.strip(",.?!;:()[]{}<>")
                lower_text = text_stripped.lower()

                # A) Ad-soyadı
                if anonymize_options.get("name") and word_in_set(lower_text, persons_set):
                    rect = fitz.Rect(x0, y0, x1, y1)
                    mask_text_aligned(
                        page=page,
                        rect=fitz.Rect(x0, y0, x1, y1),
                        font_name=font,
                        font_size=size
                    )
                    collected_data["name"].append({
                        "text": lower_text,
                        "page": page_index,
                        "bbox": [x0, y0, x1, y1],
                        "font": font,
                        "size": size
                    })

                # B) E-posta
                if anonymize_options.get("contact") and lower_text in emails_set:
                    rect = fitz.Rect(x0, y0, x1, y1)
                    mask_text_aligned(
                        page=page,
                        rect=fitz.Rect(x0, y0, x1, y1),
                        font_name=font,
                        font_size=size
                    )
                    collected_data["contact"].append({
                        "text": lower_text,
                        "page": page_index,
                        "bbox": [x0, y0, x1, y1],
                        "font": font,
                        "size": size
                    })

                # C) Kurum
                if anonymize_options.get("affiliation") and word_in_set(lower_text, orgs_set):
                    rect = fitz.Rect(x0, y0, x1, y1)
                    mask_text_aligned(
                        page=page,
                        rect=fitz.Rect(x0, y0, x1, y1),
                        font_name=font,
                        font_size=size
                    )
                    collected_data["affiliation"].append({
                        "text": lower_text,
                        "page": page_index,
                        "bbox": [x0, y0, x1, y1],
                        "font": font,
                        "size": size
                    })
        

        doc.save(output_pdf_path, garbage=4, deflate=True)
        return output_pdf_path, collected_data








class AssignReviewerView(APIView):
    """
    POST /api/articles/assign_reviewer/<str:tracking_number>/
    1) Makalenin PDF'ini parse edip classification_config.py'deki CATEGORIES'e göre alt başlıkları bulur.
    2) En çok alt başlıkla eşleşen hakemi atar.
    3) Terminalde (konsolda) her hakem için eşleşen alt başlıkları yazdırır.
    """

    def post(self, request, tracking_number, format=None):
        # 1) Makaleyi tracking_number üzerinden bul
        article = get_object_or_404(Article, tracking_number=tracking_number)

        # 2) PDF yoksa hata döndür
        if not article.pdf_file:
            return Response({'error': 'Bu makalede PDF bulunamadı.'}, status=status.HTTP_400_BAD_REQUEST)

        # 3) PDF metnini çıkar
        pdf_path = article.pdf_file.path
        text = self.extract_text_from_pdf(pdf_path)

        # 4) classification_config.py'deki CATEGORIES'e göre alt başlıkları bul
        matched_subcats = self.classify_article_text(text)
        if not matched_subcats:
            article.status = 'no_category'
            article.save()
            return Response({'warning': 'Hiçbir alt başlıkla eşleşmedi.'}, status=status.HTTP_200_OK)

        # 5) En çok alt başlıkla eşleşen hakemi bul
        best_reviewer = self.find_best_reviewer_by_subcats(matched_subcats)

        if not best_reviewer:
            article.status = 'no_reviewer'
            article.save()
            return Response({'warning': 'Uygun hakem bulunamadı.'}, status=status.HTTP_200_OK)

        # 6) Makaleyi bu hakeme ata
        article.assigned_reviewer = best_reviewer
        article.status = 'anonymized'
        article.save()

        Log.objects.create(article=article, description=f"Hakeme atandı: {best_reviewer.name}")

        # 7) Sonuç döndür
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def extract_text_from_pdf(self, pdf_path):
        """PDF dosyasının metnini birleştirerek döndürür."""
        text_content = ""
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text_content += page.get_text()
        return text_content

    def classify_article_text(self, text):
        """
        Metindeki anahtar kelimeleri arar ve classification_config içindeki
        alt başlıklar için eşleşme sayılarını hesaplar.
        Sonuç olarak, alt başlık isimlerini (lower-case) anahtar, kelime sayısını değer olarak içeren
        bir sözlük döndürür.
        """
        text_lower = text.lower()
        subcat_counts = {}
        for main_cat, subcats in CATEGORIES.items():
            for subcat_name, kw_list in subcats.items():
                count = 0
                for kw in kw_list:
                    count += text_lower.count(kw)
                if count > 0:
                    # Alt başlık ismini lower-case olarak saklıyoruz
                    subcat_counts[subcat_name.lower()] = count
        return subcat_counts

    def find_best_reviewer_by_subcats(self, subcat_counts):
        """
        subcat_counts: Örneğin, {'derin öğrenme': 12, 'doğal dil işleme': 8, ...}
        Her hakemin interests (ilgi alanları) ile subcat_counts sözlüğündeki değerler üzerinden,
        en yüksek kelime sayısına sahip olan alt başlık eşleşmesini bulur.
        Terminale her hakemin hangi alt başlıkla kaç kelime eşleştiğini yazdırır.
        En yüksek eşleşme sayısına sahip hakemi döndürür (eşleşme yoksa None).
        """
        best_reviewer = None
        best_count = 0

        for rev in Reviewer.objects.all():
            if not rev.interests:
                continue
            # Hakemin ilgi alanlarını virgülle ayırıp lower-case listesi elde edelim
            rev_interest_list = [i.strip().lower() for i in rev.interests.split(',')]
            reviewer_max = 0
            matching_subcat = None
            # Her ilgi alanı için subcat_counts içinde var mı diye kontrol edelim
            for interest in rev_interest_list:
                if interest in subcat_counts:
                    if subcat_counts[interest] > reviewer_max:
                        reviewer_max = subcat_counts[interest]
                        matching_subcat = interest
            # Debug: Terminale yazdır
            if reviewer_max > 0:
                print(f"[DEBUG] Reviewer: {rev.email}, best matching interest: {matching_subcat}, word count: {reviewer_max}")
            if reviewer_max > best_count:
                best_count = reviewer_max
                best_reviewer = rev

        return best_reviewer

class AnonymizedArticleListView(generics.ListAPIView):
    """
    GET /api/articles/anonymized/
    Anonimleştirilmiş makaleleri listeleyen API
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(status="anonymized")

class DownloadAnonymizedPDFView(APIView):
    """
    GET /api/articles/anonymized/download/<str:tracking_number>/
    Anonimleştirilmiş PDF'yi indirme API'si.
    """
    def get(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)
        if not article.anonymized_pdf_file:
            return HttpResponseNotFound("Anonimleştirilmiş PDF bulunamadı.")
        file_path = article.anonymized_pdf_file.path
        if not os.path.exists(file_path):
            return HttpResponseNotFound("Dosya bulunamadı.")
        return FileResponse(open(file_path, "rb"), content_type="application/pdf")


class LogRecordListView(generics.ListAPIView):
    queryset = Log.objects.all()
    serializer_class = LogRecordSerializer

class EvaluatedArticleListView(generics.ListAPIView):
    """
    GET /api/articles/evaluated/
    Değerlendirilmiş ve PDF'i mevcut olan makaleleri listeleyen API
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        return Article.objects.filter(
            evaluated_pdf_file__isnull=False,
            status__in=['evaluated', 'completed']
        )
    
def mask_text_aligned(page, rect, font_name, font_size):
    """
    Anonimleştirme (masking) sırasında kullanılır:
    - Verilen bounding box'u beyaza boyar
    - Kutunun genişliğine göre uygun sayıda '*' basar
    - Metni (yıldızları) kutuya sığdırmak için font boyutunu gerekirse küçültür
    """
    x0, y0, x1, y1 = rect
    width = x1 - x0
    height = y1 - y0

    # 1) Alanı beyaza boyayarak orijinal metni kapat
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

    # 2) Minimum font boyutunu belirle
    min_font = 4
    fs = max(min_font, font_size)

    # 3) Ortalama karakter genişliğine göre yıldız sayısı hesapla
    avg_char_width = fs * 0.6
    star_count = max(3, int(width / avg_char_width))
    star_text = "*" * star_count

    # 4) Metni (yıldızları) kutuya sığdırmak için font boyutunu adım adım küçült
    while fs >= min_font:
        test_rect = fitz.Rect(0, 0, width, height)
        try:
            # render_mode=3: görünmez ölçüm
            result = page.insert_textbox(
                test_rect,
                star_text,
                fontsize=fs,
                fontname=font_name,
                align=0,
                render_mode=3
            )
        except Exception:
            result = 0
        if result > 0:
            break
        fs -= 0.5

    # 5) Yıldızları gerçek şekilde bounding box içine yerleştir
    final_rect = fitz.Rect(x0, y0, x1, y1)
    page.insert_textbox(
        final_rect,
        star_text,
        fontsize=fs,
        fontname=font_name,
        color=(0, 0, 0),
        align=0
    )



def smart_insert_text_aligned(page, decrypted_text, rect, font_name, font_size, line_snap=1.5):
    """
    Geri yükleme (restore) sırasında kullanılır:
    - Verilen bounding box'a orijinal metni yerleştirir
    - Kutunun içine sığması için font boyutunu gerekirse küçültür
    - 'wrap' parametresi desteklenmediği için tek satırda kalabilir,
      çok satırlı desteği yok (veya min. deneme).
    """
    x0, y0, x1, y1 = rect
    width = x1 - x0
    height = y1 - y0

    min_font = 4
    font_size = max(min_font, font_size)

    # Geri yüklemede (restore) arka planı beyaza boyamayız;
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
    # orijinal metnin üstüne yazacağız.
    while font_size >= min_font:
        test_rect = fitz.Rect(0, 0, width, height)
        try:
            result = page.insert_textbox(
                test_rect,
                decrypted_text,
                fontsize=font_size,
                fontname=font_name,
                align=0,
                render_mode=3  # invisible measurement
            )
        except Exception:
            result = 0
        if result > 0:
            break
        font_size -= 0.5

    # Metni gerçek yerleştirme
    final_rect = fitz.Rect(x0, y0, x1, y1)
    page.insert_textbox(
        final_rect,
        decrypted_text,
        fontsize=font_size,
        fontname=font_name,
        color=(0, 0, 0),
        align=0
    )

def insert_with_original_style(page, json_entry, decrypted_text):
    """
    Geri yükleme sırasında JSON'daki bounding box, font ve boyut bilgisine göre
    'smart_insert_text_aligned' fonksiyonunu çağırarak orijinal metni kutuya yazar.
    """
    bbox = json_entry["bbox"]
    matched_font = json_entry.get("font", "helv")
    matched_size = json_entry.get("size", 10)

    rect = fitz.Rect(*bbox)
    smart_insert_text_aligned(
        page=page,
        decrypted_text=decrypted_text,
        rect=rect,
        font_name=matched_font,
        font_size=matched_size
    )












class RestoreOriginalDataView(APIView):
    """
    PDF'e yazar bilgilerini (şifre çözülerek) konumlarına göre geri ekler (IEEE uyumlu).
    """

    def post(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)

        json_path = os.path.join("media/anonymized_articles", f"{tracking_number}_enc.json")
        if not os.path.exists(json_path):
            return Response({"error": "Şifreli veri dosyası bulunamadı."}, status=status.HTTP_404_NOT_FOUND)

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                encrypted_data = json.load(f)
        except Exception as e:
            return Response({"error": f"JSON dosyası okunamadı: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(encrypted_data, dict):
            return Response({"error": "Geçersiz JSON formatı."}, status=status.HTTP_400_BAD_REQUEST)

        if all(len(items) == 0 for items in encrypted_data.values()):
            return Response({"error": "Geri yüklenecek bilgi yok. JSON verisi boş."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pdf_path = article.evaluated_pdf_file.path if article.evaluated_pdf_file else article.anonymized_pdf_file.path
            doc = fitz.open(pdf_path)

            for category, items in encrypted_data.items():
                for entry in items:
                    try:
                        encrypted_text = entry.get("encrypted") or entry.get("value")
                        page_number = entry.get("page")
                        bbox = entry.get("bbox") or entry.get("coords")

                        if not all([encrypted_text, isinstance(page_number, int), isinstance(bbox, list) and len(bbox) == 4]):
                            print(f"[SKIP] Eksik veya geçersiz alan: {entry}")
                            continue

                        decrypted = encryption.decrypt_data(encrypted_text, settings.FERNET_KEY)
                        if isinstance(decrypted, bytes):
                            decrypted = decrypted.decode("utf-8")

                        if page_number >= len(doc):
                            print(f"[SKIP] Sayfa numarası geçersiz: {page_number}")
                            continue

                        font_name = entry.get("font", "helv")
                        font_size = entry.get("size", 10)

                        rect = fitz.Rect(*bbox)

                        # IEEE formatına uygun yazı yerleştir
                        insert_with_original_style(
                            page=doc[page_number],
                            json_entry=entry,
                            decrypted_text=decrypted
                        )

                    except Exception as inner_e:
                        print(f"[ERROR] Bir öğe işlenemedi: {entry} -> {inner_e}")
                        continue

            output_path = pdf_path.replace(".pdf", "_final.pdf")
            doc.save(output_path)

            with open(output_path, "rb") as f:
                article.evaluated_pdf_file.save(f"final_{tracking_number}.pdf", ContentFile(f.read()))

            article.status = "completed"
            article.save()
            Log.objects.create(article=article, description="Yazar bilgileri PDF'e geri yüklendi.")

            return Response({
                "message": "Yazar bilgileri başarıyla geri yüklendi!",
                "file": article.evaluated_pdf_file.url
            })

        except Exception as e:
            return Response({"error": f"Geri yükleme sırasında hata: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)







class DownloadEvaluatedPDFView(APIView):
    """
    GET /api/articles/evaluated/download/<str:tracking_number>/
    Hakem değerlendirmesi tamamlanmış PDF'yi indirme API'si.
    """
    def get(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)
        if not article.evaluated_pdf_file:
            return HttpResponseNotFound("Değerlendirilmiş PDF bulunamadı.")
        
        file_path = article.evaluated_pdf_file.path
        if not os.path.exists(file_path):
            return HttpResponseNotFound("Dosya fiziksel olarak bulunamadı.")

        response = FileResponse(open(file_path, "rb"), content_type="application/pdf")
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        return response
    

class SendToAuthorView(APIView):
    """
    POST /api/articles/send_to_author/<str:tracking_number>/
    Makaleyi yazara gönderir; status alanını "sent_to_author" yapar.
    """
    def post(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)
        
        # (İsteğe bağlı) Koşulları kontrol edebilirsiniz; örneğin, sadece evaluated veya completed durumundaysa gönderme yapın.
        if article.status not in ["completed", "evaluated"]:
            return Response({"error": "Bu makale yazara gönderilemez."}, status=status.HTTP_400_BAD_REQUEST)
        
        article.status = "sent_to_author"
        article.save()
        Log.objects.create(article=article, description="Makale yazara gönderildi.")
        
        return Response({
            "message": "Makale yazara gönderildi!",
            "status": article.status,
            "file": article.evaluated_pdf_file.url if article.evaluated_pdf_file else ""
        }, status=status.HTTP_200_OK)
