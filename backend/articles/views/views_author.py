# articles/views/views_author.py
import uuid
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from ..models import Article, Log
from ..serializers import ArticleSerializer

class ArticleUploadView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        tracking_number = str(uuid.uuid4())[:8]
        instance = serializer.save(tracking_number=tracking_number)
        Log.objects.create(article=instance, description='Makale yüklendi')


class ArticleStatusQuery(APIView):
    def get(self, request, format=None):
        tracking_number = request.query_params.get('tracking_number')
        email = request.query_params.get('email')
        try:
            article = Article.objects.get(tracking_number=tracking_number, email=email)
            serializer = ArticleSerializer(article)
            return Response(serializer.data)
        except Article.DoesNotExist:
            return Response({'error': 'Makale bulunamadı'}, status=status.HTTP_404_NOT_FOUND)

class ArticleReviseView(APIView):
    # Makale revize etme
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        tracking_number = request.data.get('tracking_number')
        if not tracking_number:
            return Response({'error': 'Tracking number is required'}, status=status.HTTP_400_BAD_REQUEST)
        article = get_object_or_404(Article, tracking_number=tracking_number)
        new_pdf = request.FILES.get('pdf_file')
        if not new_pdf:
            return Response({'error': 'No PDF file provided'}, status=status.HTTP_400_BAD_REQUEST)
        article.pdf_file = new_pdf
        article.status = 'revised'
        article.save()
        Log.objects.create(article=article, description='Makale revize edildi')
        serializer = ArticleSerializer(article)
        return Response(serializer.data, status=status.HTTP_200_OK)
