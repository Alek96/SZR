from core import forms
from core.exceptions import FormNotValidError
from core.models import GitlabUser
from django import forms as django_forms
from groups import models
from groups import tasks
from groups.parser import csv_members_parse, csv_subgroup_and_members_parse


class TaskGroupForm(forms.BaseTaskGroupForm):
    class Meta(forms.BaseTaskGroupForm.Meta):
        model = models.TaskGroup

    def _pre_save(self, model, group_id=None, parent_task=None, **kwargs):
        super()._pre_save(model=model, group_id=group_id, parent_task=parent_task, **kwargs)
        if parent_task and group_id:
            raise ValueError("group_id and task_id cannot be specified at the same time")

        if parent_task:
            model.parent_task = parent_task
        elif group_id:
            model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)
        else:
            raise ValueError("group_id or task_id must be specified")


class BaseTaskForm(forms.BaseTaskForm):
    def _pre_save(self, model, group_id=None, parent_task=None, **kwargs):
        super()._pre_save(model=model, group_id=group_id, parent_task=parent_task, **kwargs)
        if not group_id and not parent_task and not model.task_group:
            raise ValueError("group_id, parent_task or task_group must be specified")

        model.parent_task = parent_task
        if group_id:
            model.gitlab_group, _ = models.GitlabGroup.objects.get_or_create(gitlab_id=group_id)


class AddSubgroupForm(BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddSubgroup
        fields = ['name', 'path', 'description', 'visibility'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id=None, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.create_subgroup(
            user_id=user_id,
            group_id=group_id,
            name=data['name'],
            path=data['path'],
            description=data['description'],
            visibility=data['visibility'],
            **kwargs)


class AddMemberForm(BaseTaskForm):
    class Meta(forms.BaseTaskForm.Meta):
        model = models.AddMember
        fields = ['username', 'access_level'] + forms.BaseTaskForm.Meta.fields

    def _save_in_gitlab(self, data, user_id, group_id, **kwargs):
        super()._save_in_gitlab(data=data, user_id=user_id, group_id=group_id, **kwargs)
        tasks.add_or_update_member(
            user_id=user_id,
            group_id=group_id,
            username=data['username'],
            access_level=data['access_level'],
            **kwargs)


class MembersFromFileForm(TaskGroupForm):
    file = django_forms.FileField()
    access_level = django_forms.TypedChoiceField(coerce=int, empty_value=None,
                                                 choices=models.AddMember.ACCESS_LEVEL_CHOICES,
                                                 initial=models.AddMember.ACCESS_GUEST)

    def _pre_save(self, **kwargs):
        super()._pre_save(**kwargs)
        try:
            self.file_data = csv_members_parse(self.files['file'].read().decode())
        except Exception as err:
            self.add_error('file', str(err))
            raise FormNotValidError(self.errors.as_data())

    def _post_save(self, model, user_id, **kwargs):
        try:
            owner = GitlabUser.objects.get(user_id=user_id)
            for member_data in self.file_data:
                models.AddMember.objects.create(
                    owner=owner,
                    task_group=model,
                    username=member_data['index'],
                    access_level=self.data['access_level']
                )
        except Exception as err:
            self.add_error('file', str(err))
            model.delete()
            raise FormNotValidError(self.errors.as_data())


class SubgroupAndMembersFromFileForm(TaskGroupForm):
    file = django_forms.FileField(label='File')
    visibility = django_forms.ChoiceField(choices=models.AddSubgroup.VISIBILITY_CHOICES,
                                          initial=models.AddSubgroup.PRIVATE)
    access_level = django_forms.TypedChoiceField(coerce=int, empty_value=None,
                                                 choices=models.AddMember.ACCESS_LEVEL_CHOICES,
                                                 initial=models.AddMember.ACCESS_GUEST)

    def _pre_save(self, **kwargs):
        super()._pre_save(**kwargs)
        try:
            self.file_data = csv_subgroup_and_members_parse(self.files['file'].read().decode())
        except Exception as err:
            self.add_error('file', str(err))
            raise FormNotValidError(self.errors.as_data())

    def _post_save(self, model, user_id, **kwargs):
        try:
            owner = GitlabUser.objects.get(user_id=user_id)
            subgroups = self.create_subgroups(model, owner)

            for member_data in self.file_data:
                for group in member_data['groups']:
                    models.AddMember.objects.create(
                        owner=owner,
                        parent_task=subgroups[group],
                        username=member_data['index'],
                        access_level=self.data['access_level']
                    )
        except Exception as err:
            self.add_error('file', str(err))
            model.delete()
            raise FormNotValidError(self.errors.as_data())

    def create_subgroups(self, model, owner):
        subgroups_dict = {}

        for member_data in self.file_data:
            for group in member_data['groups']:
                if not subgroups_dict.get(group, None):
                    subgroups_dict[group] = models.AddSubgroup.objects.create(
                        owner=owner,
                        task_group=model,
                        visibility=self.data['visibility'],
                        name=group,
                        path=group,
                    )

        return subgroups_dict
