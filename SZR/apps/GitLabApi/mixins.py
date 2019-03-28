from gitlab import exceptions as gl_exceptions

from GitLabApi.base import *
from GitLabApi.exceptions import *


class GetMixin(RESTManager):
    @on_error(gl_exceptions.GitlabGetError, GitlabGetError)
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
    @on_error(gl_exceptions.GitlabListError, GitlabListError)
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
    @on_error(gl_exceptions.GitlabCreateError, GitlabCreateError)
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
    @on_error(gl_exceptions.GitlabUpdateError, GitlabUpdateError)
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
    @on_error(gl_exceptions.GitlabDeleteError, GitlabDeleteError)
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


class ObjectDeleteMixin(RESTObject):
    @on_error(gl_exceptions.GitlabDeleteError, GitlabDeleteError)
    def delete(self, **kwargs):
        """Delete the object from the server.

        :param
            kwargs: Extra options to send to the server (e.g. sudo)

        :raise
            GitlabDeleteError: If the server cannot perform the request
        """
        self._rest_object.delete(**kwargs)


class ObjectSaveMixin(RESTObject):
    @on_error(gl_exceptions.GitlabUpdateError, GitlabUpdateError)
    def save(self, **kwargs):
        """Save the changes made to the object to the server.
        The object is updated to match what the server returns.

        :param
            kwargs: Extra options to send to the server (e.g. sudo)

        :raise
            GitlabUpdateError: If the server cannot perform the request
        """
        self._rest_object.save(**kwargs)
