from gitlab import exceptions as gl_exceptions

from GitLabApi.base import *
from GitLabApi.exceptions import *


class GetMixin(RESTManager):
    def get(self, id=None, **kwargs):
        return self._obj_cls(self._rest_manager.get(id, **kwargs))


class ListMixin(RESTManager):
    def list(self, **kwargs):
        obj = self._rest_manager.list(**kwargs)
        return [self._obj_cls(item) for item in obj]


class CreateMixin(RESTManager):

    @on_error(gl_exceptions.GitlabCreateError, GitlabCreateError)
    def create(self, data, **kwargs):
        return self._obj_cls(self._rest_manager.create(data, **kwargs))


class UpdateMixin(RESTManager):

    def update(self, id=None, new_data={}, **kwargs):
        self._rest_manager.update(id, new_data, **kwargs)


class DeleteMixin(RESTManager):

    def delete(self, id, **kwargs):
        self._rest_manager.delete(id, **kwargs)


class CRUDMixin(GetMixin, ListMixin, CreateMixin, UpdateMixin, DeleteMixin):
    pass


class ObjectDeleteMixin(RESTObject):

    def delete(self, **kwargs):
        self._rest_object.delete(**kwargs)


class ObjectSaveMixin(RESTObject):

    def save(self, **kwargs):
        self._rest_object.save(**kwargs)
