from core.tasks import BaseTask
from groups.tests import models

from SZR.celery import app as celery_app


class FakeTask(BaseTask):
    _task_model = models.FakeTask


celery_app.register_task(FakeTask())
