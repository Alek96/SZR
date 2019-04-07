from GitLabApi import exceptions
from GitLabApi.base import RESTObject, RESTManager
from gitlab import base as gl_base
from gitlab import exceptions as gl_exceptions


class GetMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabGetError, exceptions.GitlabGetError)
    def get(self, id=None, **kwargs):
        """Retrieve a single object.

        :param
            **kwargs: Extra options to send to the server (e.g. sudo)

        :return
            object: The generated RESTObject

        :raise
            GitlabGetError: If the server cannot perform the request
        """
        return self._obj_cls(self._rest_manager.get(id, **kwargs))


class ListMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabListError, exceptions.GitlabListError)
    def list(self, **kwargs):
        """Retrieve a list of objects.

        :param
            all (bool): If True, return all the items, without pagination
            per_page (int): Number of items to retrieve per request
            page (int): ID of the page to return (starts with page 1)
            as_list (bool): If set to False and no pagination option is
                defined, return a generator instead of a list
            **kwargs: Extra options to send to the server (e.g. sudo)

        :return
            list: The list of objects

        :raise
            GitlabListError: If the server cannot perform the request
        """
        obj = self._rest_manager.list(**kwargs)
        return [self._obj_cls(item) for item in obj]


class CreateMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabCreateError, exceptions.GitlabCreateError)
    def create(self, data, **kwargs):
        """Create a new object.

        :param
            data (dict): parameters to send to the server to create the
                         resource
            **kwargs: Extra options to send to the server (e.g. sudo)

        :return
            RESTObject: a new instance of the managed object class built with
                the data sent by the server

        :raise
            GitlabCreateError: If the server cannot perform the request
        """
        return self._obj_cls(self._rest_manager.create(data, **kwargs))


class UpdateMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabUpdateError, exceptions.GitlabUpdateError)
    def update(self, id=None, new_data={}, **kwargs):
        """Update an object on the server.

        :param
            id: ID of the object to update (can be None if not required)
            new_data: the update data for the object
            **kwargs: Extra options to send to the server (e.g. sudo)

        # Returns:
        #     dict: The new object data (*not* a RESTObject)

        :raise
            GitlabUpdateError: If the server cannot perform the request
        """
        self._rest_manager.update(id, new_data, **kwargs)


class DeleteMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabDeleteError, exceptions.GitlabDeleteError)
    def delete(self, id, **kwargs):
        """Delete an object on the server.

        :param
            id: ID of the object to delete
            **kwargs: Extra options to send to the server (e.g. sudo)

        :raise
            GitlabDeleteError: If the server cannot perform the request
        """
        self._rest_manager.delete(id, **kwargs)


class CRUDMixin(GetMixin, ListMixin, CreateMixin, UpdateMixin, DeleteMixin):
    pass


class AllMixin(RESTManager):
    @exceptions.on_error(gl_exceptions.GitlabListError, exceptions.GitlabListError)
    def all(self, **kwargs):
        """Retrieve a list of objects.
        gitlab.v4.objects.GroupMemberManager.all() and gitlab.v4.objects.ProjectMemberManager.all()
        returns dict, so we need convert them to objects, like in list method.
        Code is copied from gitlab.mixins.ListMixin.list

        :param
            **kwargs: Extra options to send to the server (e.g. sudo)

        :return
            list: The list of objects

        :raise
            GitlabListError: If the list could not be retrieved
        """
        obj = self._rest_manager.all(**kwargs)

        if isinstance(obj, list):
            obj_list = [self._rest_manager._obj_cls(self._rest_manager, item) for item in obj]
        else:
            obj_list = gl_base.RESTObjectList(self._rest_manager, self._rest_manager._obj_cls, obj)

        return [self._obj_cls(item) for item in obj_list]


class ObjectDeleteMixin(RESTObject):
    @exceptions.on_error(gl_exceptions.GitlabDeleteError, exceptions.GitlabDeleteError)
    def delete(self, **kwargs):
        """Delete the object from the server.

        :param
            kwargs: Extra options to send to the server (e.g. sudo)

        :raise
            GitlabDeleteError: If the server cannot perform the request
        """
        self._rest_object.delete(**kwargs)


class ObjectSaveMixin(RESTObject):
    @exceptions.on_error(gl_exceptions.GitlabUpdateError, exceptions.GitlabUpdateError)
    def save(self, **kwargs):
        """Save the changes made to the object to the server.
        The object is updated to match what the server returns.

        :param
            kwargs: Extra options to send to the server (e.g. sudo)

        :raise
            GitlabUpdateError: If the server cannot perform the request
        """
        self._rest_object.save(**kwargs)
