from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for the accounts app. This app manages custom user models and authentication."""
    default_auto_field = 'django.db.models.BigAutoField' # default primary key field type
    name = 'accounts' # custom accounts app
