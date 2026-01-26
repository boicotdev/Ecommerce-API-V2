from django.apps import AppConfig


class PurchasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'purchases'


    def ready(self):
        # This will import the signals when the app is ready
        import purchases.signals
