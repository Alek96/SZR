from __future__ import absolute_import, unicode_literals

from SZR.celery import app as celery_app
from core.tasks import BaseTask
from groups.tests import models


class FakeTask(BaseTask):
    _task_model = models.FakeAddSubgroup


celery_app.register_task(FakeTask())
