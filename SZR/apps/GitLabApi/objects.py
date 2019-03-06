# from .base import *
from .mixins import *

from gitlab import base


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


class GroupManager(CRUDMixin):
    _obj_cls = Group

    def get_roots(self):
        def _sort_by_full_name(group):
            return group.full_name

        group_list = self.list()
        group_list.sort(key=_sort_by_full_name)

        return [item for item in group_list if not item.parent_id]
