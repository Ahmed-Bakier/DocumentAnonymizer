from django.urls import path
from .views.views_reviewer import ( 
    ReviewerListView,
    ReviewerArticleListView,
    ArticleDetailView,
    ReviewerEvaluationView,
    ReviewerEvaluationsListView,
    DownloadAssignedArticleView,
)
from .views.views_editor import (  # Editörle ilgili anonimleştirme işlemleri burada
    ArticleListView,
    AnonymizeArticleView,
    AssignReviewerView,
    LogRecordListView,
    DownloadAnonymizedPDFView,
    AnonymizedArticleListView, 
    EvaluatedArticleListView,  
    RestoreOriginalDataView,
    DownloadEvaluatedPDFView,
    SendToAuthorView,
    
)
from .views import (  # Ana views.py içindeki gerekli view'leri import ettik.
    ArticleUploadView,
    ArticleStatusQuery,
    ArticleReviseView,
    MessageCreateView,
    MessageListView,
)

urlpatterns = [
    # **📌 Yazar API'leri**
    path('upload/', ArticleUploadView.as_view(), name='article-upload'),
    path('status/', ArticleStatusQuery.as_view(), name='article-status'),
    path('article/revise/', ArticleReviseView.as_view(), name='article-revise'),

    # **📌 Editör API'leri**
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/anonymized/', AnonymizedArticleListView.as_view(), name='anonymized-article-list'),
    path('articles/anonymize/<str:tracking_number>/', AnonymizeArticleView.as_view(), name='anonymize-article'),
    path('articles/assign_reviewer/<str:tracking_number>/', AssignReviewerView.as_view(), name='assign-reviewer'),
    path('articles/restore_original/<str:tracking_number>/', RestoreOriginalDataView.as_view(), name='restore-original'),  # ✅ EKLENDİ
    path('logs/', LogRecordListView.as_view(), name='log-records'),
    path('articles/evaluated/', EvaluatedArticleListView.as_view(), name='evaluated-article-list'),
    path('articles/evaluated/download/<str:tracking_number>/',DownloadEvaluatedPDFView.as_view(),name='download-evaluated'),
    path('articles/send_to_author/<str:tracking_number>/', SendToAuthorView.as_view(), name='send-to-author'),

    
    # **📌 Anonimleştirme API'leri**
    path('articles/anonymized/download/<str:tracking_number>/', DownloadAnonymizedPDFView.as_view(), name='download-anonymized'),

    # **📌 Hakem API'leri**
    path('reviewers/', ReviewerListView.as_view(), name='reviewer-list'),
    path('reviewer/articles/', ReviewerArticleListView.as_view(), name='reviewer-article-list'),
    path('reviewer/download/<str:tracking_number>/', DownloadAssignedArticleView.as_view(), name='reviewer-download'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('reviewer/evaluate/<int:pk>/', ReviewerEvaluationView.as_view(), name='reviewer-evaluate'),
    path('reviewer/evaluations/', ReviewerEvaluationsListView.as_view(), name='reviewer-evaluations'),

    # **📌 Genel API'ler**
    path('message/create/', MessageCreateView.as_view(), name='message-create'),
    path('message/list/', MessageListView.as_view(), name='message-list'),
]
