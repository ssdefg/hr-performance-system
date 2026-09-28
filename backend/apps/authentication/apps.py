from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.authentication'
    verbose_name = '인증 및 사용자 관리'

    def ready(self):
        import apps.authentication.signals
