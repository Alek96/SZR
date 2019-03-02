from httmock import HTTMock
from httmock import response
from httmock import urlmatch

import functools

from GitLabApi import GitLabContent


class MockUrlBase:
    _path = ''
    _path_prefix = '/api/v4/'
    _scheme = "http"
    _netloc = "localhost"

    def request_check(self, request, **kwargs):
        # print(request.url)
        pass

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
        return GitLabContent.get_project_list(namespace_id=1)

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.append(self.get_mock_list_url(**kwargs))
        return res


class MockGroupMembersUrls(MockUrlCRUD):
    _path = 'groups/[0-9]+/members'

    def get_get_content(self):
        return GitLabContent.get_member()

    def get_list_content(self):
        return GitLabContent.get_member_list()

    def get_all_content(self):
        return GitLabContent.get_member_all()

    def get_create_content(self):
        return GitLabContent.get_member()

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


class MockGitLabUrl(MockUrlBase):
    _mock_groups_url = MockGroupsUrls()

    def get_all_mock_urls(self, **kwargs):
        res = super().get_all_mock_urls(**kwargs)
        res.extend(self._mock_groups_url.get_all_mock_urls(**kwargs))
        return res


def mock_all_gitlab_url(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with HTTMock(*MockGitLabUrl().get_all_mock_urls()):
            return func(*args, **kwargs)

    return wrapper
