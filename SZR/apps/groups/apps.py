from django.apps import AppConfig


class GitlabWrapperConfig(AppConfig):
    name = 'groups'

    def ready(self):
        import groups.signals
