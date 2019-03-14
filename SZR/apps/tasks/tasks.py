from __future__ import absolute_import, unicode_literals
from celery import shared_task, Task

from SZR.celery import app as celery_app
from tasks.models import *


class BaseTask(Task):
    name = ''
    description = ''
    _task_model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._task = None
        self._status = None

    def __del__(self):
        self._finnish()

    def run(self, id, **kwargs):
        self._set_up(id)
        self._set_up_run()

    def _set_up(self, id):
        self._task = self._get_object_from_db(id)

    def _get_object_from_db(self, id):
        return self._task_model.objects.get(id=id)

    def _set_up_run(self):
        self._task.status = self._task.RUNNING
        if self._task.celery_task:
            self._task.celery_task.delete()
        self._task.save()

    def _finnish(self):
        if self._task:
            self._task.status = self._status
            self._task.save()


celery_app.register_task(BaseTask())
