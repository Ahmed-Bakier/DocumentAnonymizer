# articles/views/views_common.py

from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Article, Message
from ..serializers import ArticleSerializer, MessageSerializer

class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        tracking_number = self.request.data.get('tracking_number')  # <-- BURAYA DİKKAT
        sender = self.request.data.get('sender')
        message_text = self.request.data.get('message_text')

        # Makaleyi tracking_number ile arar
        article = get_object_or_404(Article, tracking_number=tracking_number)

        serializer.save(article=article, sender=sender, message_text=message_text)


class MessageListView(generics.ListAPIView):
    """
    GET /api/message/list/?tracking_number=...
    Param: tracking_number (zorunlu)
    Dönüş: [
      {
        "id": ...,
        "article": ...,
        "sender": "yazar" veya "editor",
        "message_text": "...",
        "sent_at": "2025-03-20T12:34:56Z"
      },
      ...
    ]
    """
    serializer_class = MessageSerializer

    def get_queryset(self):
        tracking_number = self.request.query_params.get('tracking_number')
        if tracking_number:
            # İlgili makalenin tüm mesajlarını (en eski en başta) sıralayarak döndür
            return Message.objects.filter(article__tracking_number=tracking_number).order_by('sent_at')
        return Message.objects.none()


class DownloadAnonymizedPDFView(APIView):
    """
    Opsiyonel: Anonimleştirilmiş PDF dosyasını indirmek için örnek endpoint.
    GET /api/article/anonymized/download/<int:pk>/
    """
    def get(self, request, pk, format=None):
        article = get_object_or_404(Article, pk=pk)
        if not hasattr(article, 'anonymized_pdf_file') or not article.anonymized_pdf_file:
            return Response({'error': 'Anonimleştirilmiş PDF bulunamadı'}, status=status.HTTP_404_NOT_FOUND)
        response = FileResponse(article.anonymized_pdf_file.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="anonymized_{article.tracking_number}.pdf"'
        return response
