from django.apps import AppConfig


class MessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'iris.messages'
    label = 'iris_messages'

    def ready(self):
        from . import signals
