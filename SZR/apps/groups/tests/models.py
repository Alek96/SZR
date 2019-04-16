from groups.models import AbstractTask


class FakeTask(AbstractTask):
    _parent_task_model = 'groups.AddSubgroup'

    def _get_task_path(self):
        return 'groups.tests.tasks.FakeTask'
