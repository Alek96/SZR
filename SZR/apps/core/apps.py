from django.apps import AppConfig
from django.db.models import signals


def call_on_class_prepared(sender, **kwargs):
    """Calls the function only if it is defined in the class being prepared"""

    try:
        sender.on_class_prepared()
    except AttributeError:
        pass


class CoreConfig(AppConfig):
    name = 'core'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        signals.class_prepared.connect(call_on_class_prepared)

    def ready(self):
        import core.signals
