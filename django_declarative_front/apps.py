from django.apps import AppConfig


class DjangoDeclarativeFrontConfig(AppConfig):
    """Django app configuration for Django Declarative Front framework."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_declarative_front'
    verbose_name = 'Django Declarative Front Framework'
    description = 'A Python web frontend framework with declarative syntax, state machines and workflow DAGs.'
    
    def ready(self):
        """Perform initialization tasks when the app is ready."""
        # Import any signals or perform initialization
        pass