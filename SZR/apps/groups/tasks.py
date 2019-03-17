from __future__ import absolute_import, unicode_literals

from core.tasks import BaseTask
from SZR.celery import app as celery_app
from groups import models


class AddGroupMemberTask(BaseTask):
    _task_model = models.AddGroupMemberTask

    def _run(self, **kwargs):
        self._status = self._task_model.COMPLETED


celery_app.register_task(AddGroupMemberTask())
