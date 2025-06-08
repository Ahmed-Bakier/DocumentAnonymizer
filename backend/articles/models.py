from django.db import models

# Yönetici (Editör) Modeli
class Editor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

# Değerlendirici (Hakem) Modeli
class Reviewer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    interests = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.name

# Makale Modeli
class Article(models.Model):
    tracking_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()  # Yazar e-posta adresi (üye olmadan yükleme)
    pdf_file = models.FileField(upload_to='articles/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # İsteğe bağlı yazar bilgileri (anonimleştirme sürecinde kullanılacak)
    author_name = models.CharField(max_length=255, blank=True, null=True)
    author_contact = models.CharField(max_length=255, blank=True, null=True)
    author_institution = models.CharField(max_length=255, blank=True, null=True)
    anonymized_pdf_file = models.FileField(upload_to='anonymized/', null=True, blank=True)  
    evaluated_pdf_file = models.FileField(upload_to='evaluated/', null=True, blank=True) 
    encrypted_metadata_path = models.CharField(max_length=255, null=True, blank=True)


    
    # Makale durumu
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('under_review', 'Under Review'),
        ('revised', 'Revised'),
        ('completed', 'Completed'),
        ('evaluated', 'Evaluated'),
        ('anonymized', 'Anonymized'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    
    # İlgili Editör ve Hakem atamaları
    assigned_editor = models.ForeignKey(Editor, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    assigned_reviewer = models.ForeignKey(Reviewer, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')

    def __str__(self):
        return f"Article {self.tracking_number}"

# Hakem Değerlendirmesi Modeli
class Review(models.Model):
    # Her makaleye ait tek bir değerlendirme (One-to-One ilişki)
    article = models.OneToOneField(Article, on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(Reviewer, on_delete=models.CASCADE, related_name='reviews')
    evaluation_text = models.TextField()
    additional_comments = models.TextField(blank=True, null=True)
    score = models.IntegerField(null=True, blank=True)  # Hakem puanı için alan
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.article.tracking_number}"

# Yazar ve Editör arası mesajlaşma için Model
class Message(models.Model):
    SENDER_CHOICES = (
        ('yazar', 'Yazar'),
        ('editor', 'Editör'),
    )
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message_text = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message for {self.article.tracking_number} from {self.sender}"

# İşlem Logları için Model
class Log(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='logs')
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Log for {self.article.tracking_number} at {self.timestamp}"
