import functools

from GitLabApi import GitLabContent
from GitLabApi import exceptions
from django.conf import settings
from httmock import HTTMock
from httmock import all_requests
from httmock import response
from httmock import urlmatch


class MockUrlBase:
    path = ''
    path_prefix = '/api/v4/'
    scheme = settings.SOCIAL_AUTH_GITLAB_API_URL[:settings.SOCIAL_AUTH_GITLAB_API_URL.index('://')]
    netloc = settings.SOCIAL_AUTH_GITLAB_API_URL[settings.SOCIAL_AUTH_GITLAB_API_URL.index('//') + 2:]

    def request_check(self, request, raise_error=None, **kwargs):
        if raise_error:
            raise raise_error

    def get_base_mock_url(self, method, path, content, **kwargs):
        path = r'^{}{}$'.format(self.path_prefix, path)

        @urlmatch(scheme=self.scheme, netloc=self.netloc, path=path, method=method)
        def mock_url(url, request):
            headers = {'Content-Type': 'application/json'}
            self.request_check(request=request, **kwargs)
            return response(200, content, headers, None, 5, request)

        return mock_url

    def get_all_mocked_urls(self, **kwargs):
        return []


class MockUrlList(MockUrlBase):
    list_content = []

    def get_mock_for_list_url(self, **kwargs):
        content = self.list_content
        path = self.path
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)


class MockUrlGet(MockUrlBase):
    get_content = {}

    def get_mock_for_get_url(self, **kwargs):
        content = self.get_content
        path = '{}/[0-9]+'.format(self.path)
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)


class MockUrlCreate(MockUrlBase):
    create_content = {}

    def get_mock_for_create_url(self, **kwargs):
        content = self.create_content
        path = self.path
        return self.get_base_mock_url(method="post", path=path, content=content, **kwargs)


class MockUrlDelete(MockUrlBase):
    delete_content = {}

    def get_mock_for_delete_url(self, **kwargs):
        content = self.delete_content
        path = '{}/[0-9]+'.format(self.path)
        return self.get_base_mock_url(method="delete", path=path, content=content, **kwargs)


class MockUrlAll(MockUrlBase):
    all_content = []

    def get_mock_for_all_url(self, **kwargs):
        content = self.all_content
        path = '{}/all'.format(self.path)
        return self.get_base_mock_url(method="get", path=path, content=content, **kwargs)


class MockUrlSave(MockUrlBase):
    save_content = {}

    def get_mock_for_save_url(self, **kwargs):
        content = self.save_content
        path = '{}/[0-9]+'.format(self.path)
        return self.get_base_mock_url(method="put", path=path, content=content, **kwargs)


class MockUrlCRUD(MockUrlList, MockUrlGet, MockUrlCreate, MockUrlDelete):
    pass


class MockGroupSubgroupsUrls(MockUrlList):
    path = 'groups/[0-9]+/subgroups'
    list_content = GitLabContent.get_group_list()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_list_url(**kwargs))
        return res


class MockGroupProjectsUrls(MockUrlList):
    path = 'groups/[0-9]+/projects'
    list_content = GitLabContent.get_group_project_list(namespace_id=1)

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_list_url(**kwargs))
        return res


class MockGroupMemberObjUrls(MockUrlSave, MockUrlDelete):
    path = 'groups/[0-9]+/members'
    save_content = GitLabContent.get_group_member()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_save_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        return res


class MockGroupMembersUrls(MockUrlCRUD, MockUrlAll):
    path = 'groups/[0-9]+/members'
    list_content = GitLabContent.get_group_member_list()
    get_content = GitLabContent.get_group_member()
    all_content = GitLabContent.get_group_member_all()
    create_content = GitLabContent.get_group_member()

    _mock_group_members_obj_url = MockGroupMemberObjUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_all_url(**kwargs))
        res.append(self.get_mock_for_list_url(**kwargs))
        res.append(self.get_mock_for_get_url(**kwargs))
        res.append(self.get_mock_for_create_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_group_members_obj_url.get_all_mocked_urls(**kwargs))
        return res


class MockGroupObjUrls(MockUrlSave, MockUrlDelete):
    path = 'groups'
    save_content = GitLabContent.get_group()

    _mock_group_subgroups_url = MockGroupSubgroupsUrls()
    _mock_group_projects_url = MockGroupProjectsUrls()
    _mock_group_members_url = MockGroupMembersUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_save_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_group_subgroups_url.get_all_mocked_urls(**kwargs))
        res.extend(self._mock_group_projects_url.get_all_mocked_urls(**kwargs))
        res.extend(self._mock_group_members_url.get_all_mocked_urls(**kwargs))
        return res


class MockGroupsUrls(MockUrlCRUD):
    path = 'groups'
    list_content = GitLabContent.get_group_list() + GitLabContent.get_subgroup_list(parent_id=1)
    get_content = GitLabContent.get_group()
    roots_content = GitLabContent.get_group_list()
    create_content = GitLabContent.get_group()

    _mock_group_obj_url = MockGroupObjUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_list_url(**kwargs))
        res.append(self.get_mock_for_get_url(**kwargs))
        res.append(self.get_mock_for_create_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_group_obj_url.get_all_mocked_urls(**kwargs))
        return res


class MockUserObjUrls(MockUrlSave, MockUrlDelete):
    path = 'users'
    save_content = GitLabContent.get_user()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_save_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        return res


class MockUsersUrls(MockUrlCRUD):
    path = 'users'
    list_content = GitLabContent.get_user_list()
    get_content = GitLabContent.get_user()
    create_content = GitLabContent.get_user()

    _mock_user_obj_url = MockUserObjUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_list_url(**kwargs))
        res.append(self.get_mock_for_get_url(**kwargs))
        res.append(self.get_mock_for_create_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_user_obj_url.get_all_mocked_urls(**kwargs))
        return res


class MockProjectMemberObjUrls(MockUrlSave, MockUrlDelete):
    path = 'projects/[0-9]+/members'
    save_content = GitLabContent.get_project_member()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_save_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        return res


class MockProjectMembersUrls(MockUrlCRUD, MockUrlAll):
    path = 'projects/[0-9]+/members'
    list_content = GitLabContent.get_project_member_list()
    get_content = GitLabContent.get_project_member()
    all_content = GitLabContent.get_project_member_all()
    create_content = GitLabContent.get_project_member()

    _mock_project_members_obj_url = MockProjectMemberObjUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_all_url(**kwargs))
        res.append(self.get_mock_for_list_url(**kwargs))
        res.append(self.get_mock_for_get_url(**kwargs))
        res.append(self.get_mock_for_create_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_project_members_obj_url.get_all_mocked_urls(**kwargs))
        return res


class MockProjectObjUrls(MockUrlSave, MockUrlDelete):
    path = 'projects'
    save_content = GitLabContent.get_project()

    _mock_project_members_url = MockProjectMembersUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_save_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_project_members_url.get_all_mocked_urls(**kwargs))
        return res


class MockProjectsUrls(MockUrlCRUD):
    path = 'projects'
    list_content = GitLabContent.get_project_list()
    get_content = GitLabContent.get_project()
    create_content = GitLabContent.get_project()

    _mock_project_obj_url = MockProjectObjUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.append(self.get_mock_for_list_url(**kwargs))
        res.append(self.get_mock_for_get_url(**kwargs))
        res.append(self.get_mock_for_create_url(**kwargs))
        res.append(self.get_mock_for_delete_url(**kwargs))
        res.extend(self._mock_project_obj_url.get_all_mocked_urls(**kwargs))
        return res


@all_requests
def mock_all_urls_and_raise_error(url, request):
    raise exceptions.NoMockedUrlError("Url '{}' is not mocked".format(url))


class MockGitLabUrl(MockUrlBase):
    _mock_groups_url = MockGroupsUrls()
    _mock_users_url = MockUsersUrls()
    _mock_projects_url = MockProjectsUrls()

    def get_all_mocked_urls(self, **kwargs):
        res = super().get_all_mocked_urls(**kwargs)
        res.extend(self._mock_groups_url.get_all_mocked_urls(**kwargs))
        res.extend(self._mock_users_url.get_all_mocked_urls(**kwargs))
        res.extend(self._mock_projects_url.get_all_mocked_urls(**kwargs))

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
        with HTTMock(*MockGitLabUrl().get_all_mocked_urls(**wrapped_kwargs)):
            return func(*args, **kwargs)

    return wrapped_f
