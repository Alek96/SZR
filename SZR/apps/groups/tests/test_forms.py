from GitLabApi import mock_all_gitlab_url
from core.tests.test_view import LoginMethods
from django import forms
from groups import forms
from groups import models
from groups.tests.forms import FakeTaskGroupForm, FakeTaskGroup
from groups.tests.test_models import AddSubgroupCreateMethods, AddMemberCreateMethods, AbstractTaskGroupCreateMethods


class BaseTaskGroupFormTests(LoginMethods):
    form_class = FakeTaskGroupForm
    model_class = FakeTaskGroup
    parent_create_methods = AbstractTaskGroupCreateMethods
    valid_form_data = {
        'name': "name",
    }

    def test_save(self):
        form = self.form_class(self.valid_form_data)
        with self.assertRaises(ValueError):
            form.save()

    def test_save_with_group_id(self):
        form = self.form_class(self.valid_form_data)
        form.save(group_id=1)

        task_group = self.model_class.objects.get(id=1)
        self.assertEqual(task_group.gitlab_group_id, 1)

    def test_save_with_task_id(self):
        task = self.parent_create_methods().create_parent_task()
        form = self.form_class(self.valid_form_data)
        task_group = form.save(task_id=task.id)

        self.assertEqual(task_group.parent_task.id, task.id)


class AddSubgroupGroupFormTests(BaseTaskGroupFormTests):
    form_class = forms.AddSubgroupGroupForm
    model_class = models.AddSubgroupGroup
    parent_create_methods = AddSubgroupCreateMethods
    valid_form_data = {
        'name': "name",
    }


class AddSubgroupFormTests(LoginMethods):
    valid_form_data = {
        'name': "Group_name",
        'path': "Group_path",
        'description': "Description",
        'visibility': models.AddSubgroup.PRIVATE,
    }

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddSubgroupForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = forms.AddSubgroupForm(self.valid_form_data)
        task_group = AddSubgroupCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group_id=task_group.id)

        task = models.AddSubgroup.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)


class AddMemberGroupFormTests(BaseTaskGroupFormTests):
    form_class = forms.AddMemberGroupForm
    model_class = models.AddMemberGroup
    parent_create_methods = AddSubgroupCreateMethods
    valid_form_data = {
        'name': "name",
    }
    mandatory_fields = ['name']


class AddMemberFormTests(LoginMethods):
    valid_form_data = {
        'username': "username",
        'access_level': models.AddMember.ACCESS_GUEST,
    }

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_save_in_gitlab(self):
        form = forms.AddMemberForm(self.valid_form_data)
        form.save_in_gitlab(user_id=self.user.id, group_id=1)

    @LoginMethods.create_user_wrapper
    def test_save(self):
        form = forms.AddMemberForm(self.valid_form_data)
        task_group = AddMemberCreateMethods().create_task_group()
        form.save(user_id=self.user.id, task_group_id=task_group.id)

        task = models.AddMember.objects.get(task_group=task_group)
        for key, value in self.valid_form_data.items():
            self.assertEqual(getattr(task, key), value)
        self.assertEqual(task.owner_id, self.user.id)
