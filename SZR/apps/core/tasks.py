from __future__ import absolute_import, unicode_literals
from celery import shared_task, Task
from django.conf import settings
from django.utils import timezone


class BaseTask(Task):
    name = ''
    description = ''
    _task_model = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = '{0}.{1}'.format(self.__module__, self.__name__)

    def run(self, task_id, **kwargs):
        self._set_up(task_id)
        self._set_up_run()
        self._run(**kwargs)
        self._finnish()

    def _run(self, **kwargs):
        raise NotImplementedError('Task must define the _run method.')

    def _set_up(self, task_id):
        self._task = self._get_object_from_db(task_id)

    def _get_object_from_db(self, task_id):
        return self._task_model.objects.get(id=task_id)

    def _set_up_run(self):
        self._task.celery_task.delete()
        self._task.celery_task = None
        self._task.status = self._task.RUNNING
        self._task.save()

    def _finnish(self):
        self._task.status = self._status
        self._task.finished_date = timezone.now()
        self._task.save()

        self._task.task_group.increment_finished_tasks_number(self._status)
        self._task.task_group.save()
