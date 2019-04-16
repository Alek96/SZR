from GitLabApi import mock_all_gitlab_url
from core.tests.test_view import LoginMethods
from django import forms
from groups import forms
from groups import models
from groups.tests.forms import FakeTaskForm
from groups.tests.models import FakeTask
from groups.tests.test_models import AddSubgroupCreateMethods, AddMemberCreateMethods, AbstractTaskCreateMethods
from core.tests import test_forms


class TaskGroupFormTests(test_forms.BaseTaskGroupFormTest):
    form_class = forms.TaskGroupForm
    model_class = models.TaskGroup
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = ['name']
    readonly_fields = ['finished_date']

    def create_model(self, status=None, **kwargs):
        create_methods = AbstractTaskCreateMethods()
        task_group = create_methods.create_task_group(**kwargs)

        if status == self.model_class.SUCCEED:
            create_methods.create_task(task_group=task_group, status=status)

        return task_group

    def test_save(self):
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save()

    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data)
        form.save(group_id=1)

        task_group = self.model_class.objects.get(id=1)
        self.assertEqual(task_group.gitlab_group_id, 1)

    def test_save_with_parent_task(self):
        parent_task = AbstractTaskCreateMethods().create_parent_task()
        form = self.form_class(self.valid_form_data)
        task_group = form.save(parent_task=parent_task)

        self.assertEqual(task_group.parent_task.id, parent_task.id)

    def test_save_with_group_id_and_parent_task(self):
        parent_task = AbstractTaskCreateMethods().create_parent_task()
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save(group_id=1, parent_task=parent_task)


class BaseTaskFormTest(test_forms.BaseTaskFormTest):
    form_class = FakeTaskForm
    model_class = FakeTask
    valid_form_data = {
        'name': "My Name",
    }
    mandatory_fields = []
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    def create_model(self, **kwargs):
        return AbstractTaskCreateMethods().create_task(**kwargs)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save(user_id=self.user.id)

    @LoginMethods.create_user_wrapper
    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data)
        form.save(user_id=self.user.id, group_id=1)

        task = self.model_class.objects.get(id=1)
        self.assertEqual(task.gitlab_group_id, 1)

    @LoginMethods.create_user_wrapper
    def test_save_with_parent_task(self):
        parent_task = AbstractTaskCreateMethods().create_parent_task()
        form = self.form_class(self.valid_form_data)
        task = form.save(user_id=self.user.id, parent_task=parent_task)

        self.assertEqual(task.parent_task.id, parent_task.id)


class AddSubgroupFormTests(BaseTaskFormTest):
    form_class = forms.AddSubgroupForm
    model_class = models.AddSubgroup
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': models.AddSubgroup.PRIVATE,
    }
    mandatory_fields = ['name', 'path']
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    def create_model(self, **kwargs):
        return AddSubgroupCreateMethods().create_task(**kwargs)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddSubgroupForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = forms.AddSubgroupForm(self.valid_form_data)
        task_group = AddSubgroupCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group=task_group)

        task = models.AddSubgroup.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)


class AddMemberFormTests(BaseTaskFormTest):
    form_class = forms.AddMemberForm
    model_class = models.AddMember
    valid_form_data = {
        'username': "username",
        'access_level': models.AddMember.ACCESS_GUEST,
    }
    mandatory_fields = ['username']
    readonly_fields = ['status', 'error_msg', 'execute_date', 'finished_date']

    def create_model(self, **kwargs):
        return AddMemberCreateMethods().create_task(**kwargs)

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddMemberForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = forms.AddMemberForm(self.valid_form_data)
        task_group = AddMemberCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group=task_group)

        task = models.AddMember.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)
