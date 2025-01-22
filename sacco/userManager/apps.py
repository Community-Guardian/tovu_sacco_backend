from django.apps import AppConfig


class UsermanagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'userManager'
    def ready(self):
        import userManager.signals