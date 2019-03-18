from gitlab import base

from GitLabApi.mixins import *
from GitLabApi.exceptions import *


class GroupSubgroup(RESTObject):
    pass


class GroupSubgroupManager(ListMixin):
    _obj_cls = GroupSubgroup


class GroupProject(RESTObject):
    pass


class GroupProjectManager(ListMixin):
    _obj_cls = GroupProject


class GroupMember(ObjectSaveMixin, ObjectDeleteMixin):
    pass


class GroupMemberManager(CRUDMixin):
    _obj_cls = GroupMember

    def all(self, **kwargs):

        """
        gitlab.v4.objects.GroupMemberManager.all() returns dict, so we need convert them to objects, like in list method
        Code is copied from gitlab.mixins.ListMixin.list
        """
        obj = self._rest_manager.all(**kwargs)

        if isinstance(obj, list):
            obj_list = [self._rest_manager._obj_cls(self._rest_manager, item) for item in obj]
        else:
            obj_list = base.RESTObjectList(self._rest_manager, self._rest_manager._obj_cls, obj)

        return [self._obj_cls(item) for item in obj_list]

    def external(self, **kwargs):
        internal = self.list()
        all_members = self.all()

        external = []
        for member in all_members:
            exist = False
            for i in internal:
                if member.id == i.id:
                    exist = True
                    break
            if not exist:
                external.append(member)

        return external


class Group(ObjectSaveMixin, ObjectDeleteMixin):
    def __init__(self, rest_object):
        super().__init__(rest_object)
        self.__dict__.update({
            'subgroups': GroupSubgroupManager(rest_object.subgroups),
            'projects': GroupProjectManager(rest_object.projects),
            'members': GroupMemberManager(rest_object.members),
        })

    def save(self, **kwargs):
        """
        if visibility level is not specified, server will set it to public, overwriting current visibility level.
        """
        self.visibility = getattr(self, 'visibility')
        super().save(**kwargs)


class GroupManager(CRUDMixin):
    _obj_cls = Group

    def get_roots(self):
        def _sort_by_full_name(group):
            return group.full_name

        group_list = self.list()
        group_list.sort(key=_sort_by_full_name)

        return [item for item in group_list if not item.parent_id]


class User(ObjectSaveMixin, ObjectDeleteMixin):

    def save(self, **kwargs):
        """
        This method in gitlab module need email to save obj, but GitLab server does not sand as this information.
        """
        raise NotImplementedError("gitlab module does not have working method")


class UserManager(CRUDMixin):
    _obj_cls = User

    def get(self, id=None, username=None, **kwargs):
        """
        Can get user by its username
        """
        if not username:
            return super().get(id, **kwargs)
        else:
            user = self.list(username=username)
            if not user:
                raise GitlabGetError(error_message='Failed to get user {"username": ["Does not exist"]}')
            return user[0]


class ProjectMember(ObjectSaveMixin, ObjectDeleteMixin):
    pass


class ProjectMemberManager(CRUDMixin):
    _obj_cls = ProjectMember

    def all(self, **kwargs):

        """
        gitlab.v4.objects.ProjectMemberManager.all() returns dict, so we need convert them to objects, like in list method
        Code is copied from gitlab.mixins.ListMixin.list
        """
        obj = self._rest_manager.all(**kwargs)

        if isinstance(obj, list):
            obj_list = [self._rest_manager._obj_cls(self._rest_manager, item) for item in obj]
        else:
            obj_list = base.RESTObjectList(self._rest_manager, self._rest_manager._obj_cls, obj)

        return [self._obj_cls(item) for item in obj_list]

    def external(self, **kwargs):
        internal = self.list()
        all_members = self.all()

        external = []
        for member in all_members:
            exist = False
            for i in internal:
                if member.id == i.id:
                    exist = True
                    break
            if not exist:
                external.append(member)

        return external


class Project(ObjectSaveMixin, ObjectDeleteMixin):
    def __init__(self, rest_object):
        super().__init__(rest_object)
        self.__dict__.update({
            'members': ProjectMemberManager(rest_object.members),
        })

    def save(self, **kwargs):
        """
        if visibility level is not specified, server will set it to public, overwriting current visibility level.
        """
        self.visibility = getattr(self, 'visibility')
        super().save(**kwargs)


class ProjectManager(CRUDMixin):
    _obj_cls = Project
