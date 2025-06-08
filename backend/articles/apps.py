from django.apps import AppConfig

class ArticlesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "articles"

    def ready(self):
        import articles.serializers  # Ensure this is not registering models again
