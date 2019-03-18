from django.conf import settings

from httmock import HTTMock
from httmock import response
from httmock import urlmatch
from httmock import all_requests

import functools

from GitLabApi import GitLabContent
from GitLabApi import exceptions


class MockUrlBase:
    _path = ''
    _path_prefix = '/api/v4/'
    _scheme = settings.SOCIAL_AUTH_GITLAB_API_URL[:settings.SOCIAL_AUTH_GITLAB_API_URL.index('://')]
    _netloc = settings.SOCIAL_AUTH_GITLAB_API_URL[settings.SOCIAL_AUTH_GITLAB_API_URL.index('//') + 2:]

    def request_check(self, request, raise_error=None, **kwargs):
        if raise_error:
            raise raise_error

    def get_base_mock_url(self, method, path, content, **kwargs):
        path = r'^{}{}$'.format(self._path_prefix, path)

        @urlmatch(scheme=self._scheme, netloc=self._netloc, path=path, method=method)
        def mock_url(url, request):
            headers = {'Content-Type': 'application/json'}
            self.request_check(request=request, **kwargs)
            return response(200, content, headers, None, 5, request)

        return mock_url

    def get_all_mock_urls(self, **kwargs):
        return []


class MockUrlList(MockUrlBase):
    def get_mock_list_url(self, **kwargs):
        content = self.get_list_content()
        path = self._path
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)

    def get_list_content(self):
        return []


class MockUrlGet(MockUrlBase):
    def get_mock_get_url(self, **kwargs):
        content = self.get_get_content()
        path = '{}/[0-9]+'.format(self._path)
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)

    def get_get_content(self):
        return {}


class MockUrlCreate(MockUrlBase):
    def get_mock_create_url(self, **kwargs):
        content = self.get_create_content()
        path = self._path
        return self.get_base_mock_url(method="post", path=path, content=content, **kwargs)

    def get_create_content(self):
        return {}


class MockUrlDelete(MockUrlBase):
    def get_mock_delete_url(self, **kwargs):
        content = self.get_delete_content()
        path = '{}/[0-9]+'.format(self._path)
        return self.get_base_mock_url(method="delete", path=path, content=content, **kwargs)

    def get_delete_content(self):
        return {}


class MockUrlSave(MockUrlBase):
    def get_mock_save_url(self, **kwargs):
        content = self.get_save_content()
        path = '{}/[0-9]+'.format(self._path)
        return self.get_base_mock_url(method="put", path=path, content=content, **kwargs)

    def get_save_content(self):
        return {}


class MockUrlCRUD(MockUrlList, MockUrlGet, MockUrlCreate, MockUrlDelete):
    pass


class MockGroupSubgroupsUrls(MockUrlList):
    _path = 'groups/[0-9]+/subgroups'

    def get_list_content(self):
        return GitLabContent.get_group_list()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        return res


class MockGroupProjectsUrls(MockUrlList):
    _path = 'groups/[0-9]+/projects'

    def get_list_content(self):
        return GitLabContent.get_group_project_list(namespace_id=1)

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        return res


class MockGroupMemberObjUrls(MockUrlSave, MockUrlDelete):
    _path = 'groups/[0-9]+/members'

    def get_save_content(self):
        return GitLabContent.get_group_member()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_save_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        return res


class MockGroupMembersUrls(MockUrlCRUD):
    _path = 'groups/[0-9]+/members'
    _mock_group_members_obj_url = MockGroupMemberObjUrls()

    def get_get_content(self):
        return GitLabContent.get_group_member()

    def get_list_content(self):
        return GitLabContent.get_group_member_list()

    def get_all_content(self):
        return GitLabContent.get_group_member_all()

    def get_create_content(self):
        return GitLabContent.get_group_member()

    def get_mock_all_url(self, **kwargs):
        content = self.get_all_content()
        path = '{}/all'.format(self._path)
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_all_url(**kwargs))
        res.append(self.get_mock_list_url(**kwargs))
        res.append(self.get_mock_get_url(**kwargs))
        res.append(self.get_mock_create_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_group_members_obj_url.get_all_mock_urls(**kwargs))
        return res


class MockGroupObjUrls(MockUrlSave, MockUrlDelete):
    _path = 'groups'
    _mock_group_subgroups_url = MockGroupSubgroupsUrls()
    _mock_group_projects_url = MockGroupProjectsUrls()
    _mock_group_members_url = MockGroupMembersUrls()

    def get_save_content(self):
        return GitLabContent.get_group()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_save_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_group_subgroups_url.get_all_mock_urls(**kwargs))
        res.extend(self._mock_group_projects_url.get_all_mock_urls(**kwargs))
        res.extend(self._mock_group_members_url.get_all_mock_urls(**kwargs))
        return res


class MockGroupsUrls(MockUrlCRUD):
    _path = 'groups'
    _mock_group_obj_url = MockGroupObjUrls()

    def get_get_content(self):
        return GitLabContent.get_group()

    def get_list_content(self):
        group_list_content = self.get_roots_content()
        subgroup_list_content = GitLabContent.get_subgroup_list(parent_id=1)
        return group_list_content + subgroup_list_content

    def get_roots_content(self):
        return GitLabContent.get_group_list()

    def get_create_content(self):
        return GitLabContent.get_group()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        res.append(self.get_mock_get_url(**kwargs))
        res.append(self.get_mock_create_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_group_obj_url.get_all_mock_urls(**kwargs))
        return res


class MockUserObjUrls(MockUrlSave, MockUrlDelete):
    _path = 'users'

    def get_save_content(self):
        return GitLabContent.get_user()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_save_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        return res


class MockUsersUrls(MockUrlCRUD):
    _path = 'users'
    _mock_user_obj_url = MockUserObjUrls()

    def get_get_content(self):
        return GitLabContent.get_user()

    def get_list_content(self):
        return GitLabContent.get_user_list()

    def get_create_content(self):
        return GitLabContent.get_user()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        res.append(self.get_mock_get_url(**kwargs))
        res.append(self.get_mock_create_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_user_obj_url.get_all_mock_urls(**kwargs))
        return res


class MockProjectMemberObjUrls(MockUrlSave, MockUrlDelete):
    _path = 'projects/[0-9]+/members'

    def get_save_content(self):
        return GitLabContent.get_project_member()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_save_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        return res


class MockProjectMembersUrls(MockUrlCRUD):
    _path = 'projects/[0-9]+/members'
    _mock_project_members_obj_url = MockProjectMemberObjUrls()

    def get_get_content(self):
        return GitLabContent.get_project_member()

    def get_list_content(self):
        return GitLabContent.get_project_member_list()

    def get_all_content(self):
        return GitLabContent.get_project_member_all()

    def get_create_content(self):
        return GitLabContent.get_project_member()

    def get_mock_all_url(self, **kwargs):
        content = self.get_all_content()
        path = '{}/all'.format(self._path)
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_all_url(**kwargs))
        res.append(self.get_mock_list_url(**kwargs))
        res.append(self.get_mock_get_url(**kwargs))
        res.append(self.get_mock_create_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_project_members_obj_url.get_all_mock_urls(**kwargs))
        return res


class MockProjectObjUrls(MockUrlSave, MockUrlDelete):
    _path = 'projects'
    _mock_project_members_url = MockProjectMembersUrls()

    def get_save_content(self):
        return GitLabContent.get_project()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_save_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_project_members_url.get_all_mock_urls(**kwargs))
        return res


class MockProjectsUrls(MockUrlCRUD):
    _path = 'projects'
    _mock_project_obj_url = MockProjectObjUrls()

    def get_get_content(self):
        return GitLabContent.get_project()

    def get_list_content(self):
        return GitLabContent.get_project_list()

    def get_create_content(self):
        return GitLabContent.get_project()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        res.append(self.get_mock_get_url(**kwargs))
        res.append(self.get_mock_create_url(**kwargs))
        res.append(self.get_mock_delete_url(**kwargs))
        res.extend(self._mock_project_obj_url.get_all_mock_urls(**kwargs))
        return res


@all_requests
def mock_all_urls_and_raise_error(url, request):
    raise exceptions.NoMockedUrlError("Url '{}' is not mocked".format(url))


class MockGitLabUrl(MockUrlBase):
    _mock_groups_url = MockGroupsUrls()
    _mock_users_url = MockUsersUrls()
    _mock_projects_url = MockProjectsUrls()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.extend(self._mock_groups_url.get_all_mock_urls(**kwargs))
        res.extend(self._mock_users_url.get_all_mock_urls(**kwargs))
        res.extend(self._mock_projects_url.get_all_mock_urls(**kwargs))

        res.append(mock_all_urls_and_raise_error)
        return res


def mock_all_gitlab_url(func=None, **wrapped_kwargs):
    """

    :param func: Wrapped function
    :param raise_error: Error to raise
    :return:
    """
    if func is None:
        return functools.partial(mock_all_gitlab_url, **wrapped_kwargs)

    @functools.wraps(func)
    def wrapped_f(*args, **kwargs):
        with HTTMock(*MockGitLabUrl().get_all_mock_urls(**wrapped_kwargs)):
            return func(*args, **kwargs)

    return wrapped_f
