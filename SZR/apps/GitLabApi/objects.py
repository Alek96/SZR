from GitLabApi import mixins
from GitLabApi.exceptions import GitlabGetError
from django.utils.translation import gettext_lazy as _


class ChoiceAttribute:
    def _get_field_readable(self, field, choices):
        return dict(choices).get(field, field)


class AccessLevel(ChoiceAttribute):
    ACCESS_GUEST = 10
    ACCESS_REPORTER = 20
    ACCESS_DEVELOPER = 30
    ACCESS_MASTER = 40
    ACCESS_OWNER = 50
    ACCESS_LEVEL_CHOICES = (
        (ACCESS_GUEST, _('Guest')),
        (ACCESS_REPORTER, _('Reporter')),
        (ACCESS_DEVELOPER, _('Developer')),
        (ACCESS_MASTER, _('Master')),
        (ACCESS_OWNER, _('Owner')),
    )

    def get_access_level_readable(self):
        return self._get_field_readable(getattr(self, 'access_level', None), self.ACCESS_LEVEL_CHOICES)


class VisibilityLevel(ChoiceAttribute):
    PRIVATE = 'private'
    Internal = 'internal'
    PUBLIC = 'public'
    VISIBILITY_CHOICES = (
        (PRIVATE, _('Private')),
        (Internal, _('Internal')),
        (PUBLIC, _('Public')),
    )

    def get_visibility_readable(self):
        return self._get_field_readable(getattr(self, 'visibility', None), self.VISIBILITY_CHOICES)


class GroupSubgroup(mixins.RESTObject, VisibilityLevel):
    pass


class GroupSubgroupManager(mixins.ListMixin):
    _obj_cls = GroupSubgroup


class GroupProject(mixins.RESTObject, VisibilityLevel):
    pass


class GroupProjectManager(mixins.ListMixin):
    _obj_cls = GroupProject


class GroupMember(mixins.ObjectSaveMixin, mixins.ObjectDeleteMixin, AccessLevel):
    pass


class GroupMemberManager(mixins.CRUDMixin, mixins.AllMixin):
    _obj_cls = GroupMember

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


class Group(mixins.ObjectSaveMixin, mixins.ObjectDeleteMixin, VisibilityLevel):
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


class GroupManager(mixins.CRUDMixin):
    _obj_cls = Group

    def get_roots(self):
        def _sort_by_full_name(group):
            return group.full_name

        group_list = self.list()
        group_list.sort(key=_sort_by_full_name)

        return [item for item in group_list if not item.parent_id]


class User(mixins.ObjectSaveMixin, mixins.ObjectDeleteMixin):

    def save(self, **kwargs):
        """
        This method in gitlab module need email to save obj, but GitLab server does not sand as this information.
        """
        raise NotImplementedError("gitlab module does not have working method")


class UserManager(mixins.CRUDMixin):
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


class ProjectMember(mixins.ObjectSaveMixin, mixins.ObjectDeleteMixin, AccessLevel):
    pass


class ProjectMemberManager(mixins.CRUDMixin, mixins.AllMixin):
    _obj_cls = ProjectMember

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


class Project(mixins.ObjectSaveMixin, mixins.ObjectDeleteMixin, VisibilityLevel):
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


class ProjectManager(mixins.CRUDMixin):
    _obj_cls = Project
