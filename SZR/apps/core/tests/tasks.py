from core.tasks import BaseTask
from core.tests import models

from SZR.celery import app as celery_app


class FakeTask(BaseTask):
    _task_model = models.FakeTask

    def _run(self, **kwargs):
        pass


celery_app.register_task(FakeTask())
