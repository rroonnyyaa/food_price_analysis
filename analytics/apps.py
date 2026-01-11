from django.apps import AppConfig
from django.db.models.signals import post_migrate

def seed_data(sender, **kwargs):
    from django.core.management import call_command
    try:
        call_command('seed_db')
    except Exception as e:
        pass # Handle case where tables don't exist yet or other errors

class AnalyticsConfig(AppConfig):
    name = "analytics"

    def ready(self):
        import analytics.crud
        post_migrate.connect(seed_data, sender=self)
