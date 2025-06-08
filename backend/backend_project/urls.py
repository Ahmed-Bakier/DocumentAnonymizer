from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URL'ini kaldırdık, çünkü 'django.contrib.admin' INSTALLED_APPS'ta yok.
    # path('admin/', admin.site.urls),
    
    # Uygulama URL'lerini ekleyebilirsiniz:
    path('api/', include('articles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)