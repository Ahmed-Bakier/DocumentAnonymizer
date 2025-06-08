# articles/views/views_reviewer.py

from django.http import FileResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from django.utils import timezone
from ..models import Article, Log, Reviewer, Review 
from ..serializers import ArticleSerializer, ReviewerSerializer

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.conf import settings


def append_review_to_pdf(original_pdf_path, output_pdf_path, reviewer_name, score, feedback):
    reader = PdfReader(original_pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    # Yeni sayfa oluştur
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 12)
    can.drawString(50, 750, "Reviewer Evaluation Report")
    can.drawString(50, 720, f"Reviewer: {reviewer_name}")
    can.drawString(50, 700, f"Score: {score}/10")
    can.drawString(50, 680, "Feedback:")
    y = 660
    for line in feedback.split('\n'):
        can.drawString(70, y, line)
        y -= 20
    can.save()
    packet.seek(0)
    new_pdf = PdfReader(packet)
    writer.add_page(new_pdf.pages[0])

    with open(output_pdf_path, "wb") as f:
        writer.write(f)

class ReviewerListView(generics.ListAPIView):
    """
    GET /api/reviewers/
    Tüm hakemleri listeleyen endpoint.
    """
    queryset = Reviewer.objects.all()
    serializer_class = ReviewerSerializer


class ReviewerArticleListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        reviewer_id = self.request.query_params.get('reviewer')
        if reviewer_id:
            return Article.objects.filter(assigned_reviewer__id=reviewer_id)
        return Article.objects.none()


class ArticleDetailView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer



class ReviewerEvaluationView(APIView):
    def post(self, request, pk, format=None):
        article = get_object_or_404(Article, pk=pk)
        feedback = request.data.get('reviewer_feedback')
        score = request.data.get('score')
        reviewer_id = request.data.get('reviewer_id')

        if not feedback or not score or not reviewer_id:
            return Response({"error": "Zorunlu alanlar eksik."}, status=400)

        review, created = Review.objects.get_or_create(
            article_id=article.id,
            defaults={
                'reviewer_id': reviewer_id,
                'evaluation_text': feedback,
                'score': score,
                'created_at': timezone.now()
            }
        )

        if not created:
            review.reviewer_id = reviewer_id
            review.evaluation_text = feedback
            review.score = score
            review.created_at = timezone.now()
            review.save()

        article.status = 'evaluated'
        article.save()
        Log.objects.create(article=article, description='Hakem değerlendirmesi eklendi.')

        # PDF'e değerlendirme sayfası ekle
        if article.anonymized_pdf_file:
            reviewer = Reviewer.objects.get(id=reviewer_id)
            original_path = article.anonymized_pdf_file.path
            filename = f"{article.tracking_number}_evaluated.pdf"
            evaluated_path = os.path.join(settings.MEDIA_ROOT, 'evaluated', filename)

            append_review_to_pdf(
                original_pdf_path=original_path,
                output_pdf_path=evaluated_path,
                reviewer_name=reviewer.name,
                score=score,
                feedback=feedback
            )

            # Dosya yolunu kaydet
            article.evaluated_pdf_file.name = f"evaluated/{filename}"
            article.save()

        return Response({"message": "Değerlendirme ve PDF başarıyla eklendi."})

class ReviewerEvaluationsListView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        reviewer = self.request.query_params.get('reviewer')
        return Article.objects.filter(assigned_reviewer=reviewer, status='evaluated')


class DownloadAssignedArticleView(APIView):
    """
    GET /api/reviewer/download/<str:tracking_number>/
    Hakemin kendisine atanmış anonimleştirilmiş makaleyi indirmesi için API.
    """
    def get(self, request, tracking_number, format=None):
        article = get_object_or_404(Article, tracking_number=tracking_number)
        
        if not article.anonymized_pdf_file:
            return HttpResponseNotFound("Anonimleştirilmiş PDF bulunamadı.")
        
        file_path = article.anonymized_pdf_file.path

        if not os.path.exists(file_path):
            return HttpResponseNotFound("Dosya bulunamadı.")

        return FileResponse(open(file_path, "rb"), content_type="application/pdf")