from django.apps import AppConfig


class TimesheetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # 64-bit integer for primary keys
    name = 'timesheets'

    def ready(self):
        import timesheets.signals

