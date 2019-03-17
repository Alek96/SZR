from core.tests.test_tasks import BaseTaskTestCase
from groups.tasks import AddGroupMemberTask
from groups.tests.test_models import AddGroupMemberTaskGroupAndTaskMethods


class AddGroupMemberTaskTests(BaseTaskTestCase.BaseTaskTests):
    _task_cls = AddGroupMemberTask
    _task_group_and_task_methods_class = AddGroupMemberTaskGroupAndTaskMethods
