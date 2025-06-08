# articles/serializers.py
from rest_framework import serializers
from .models import Article, Reviewer, Log, Message  
# Örnek import

class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviewer
        fields = '__all__' 

class ArticleSerializer(serializers.ModelSerializer):
    assigned_reviewer = ReviewerSerializer(read_only=True)  
    # Bu satır, assigned_reviewer alanını tam Reviewer objesi olarak döndürür.

    class Meta:
        model = Article
        fields = '__all__'
        extra_kwargs = {
            'tracking_number': {'read_only': True},
        }


class ReviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviewer
        fields = '__all__'

class LogRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    
    article = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'article', 'sender', 'message_text', 'sent_at']
        
        read_only_fields = ['id', 'article', 'sent_at']