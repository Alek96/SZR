from celery import Task
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
        try:
            self._run(**kwargs)
            self._task.status = self._task.SUCCEED
        except Exception as err:
            self._task.error_msg = str(err)
            self._task.status = self._task.FAILED
        self._finnish()

    def _run(self, **kwargs):
        raise NotImplementedError('Task must define the _run method.')

    def _set_up(self, task_id):
        self._task = self._get_object_from_db(task_id)
        self._task.status = self._task.RUNNING
        self._task.save()

    def _get_object_from_db(self, task_id):
        return self._task_model.objects.get(id=task_id)

    def _finnish(self):
        self._task.finished_date = timezone.now()
        self._task.save()
