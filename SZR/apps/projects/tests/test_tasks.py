import json

from GitLabApi import mock_all_gitlab_url
from GitLabApi.MockUrls import mock_all_urls_and_raise_error
from GitLabApi.exceptions import GitlabGetError
from core.models import GitlabUser
from core.tests.test_view import LoginMethods
from httmock import HTTMock
from projects import tasks
from projects.tests.models import AddMemberCreateMethods


class AddOrUpdateMemberTests(LoginMethods):

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_update_user(self):
        from GitLabApi.tests.test_gitlab_api import TestGitLabProjectsApi, TestGitLabUsersApi, \
            TestGitLabProjectMembersApi, TestGitLabProjectMemberObjApi

        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabProjectsApi().get_mock_for_get_url()):
                with HTTMock(TestGitLabUsersApi().get_mock_for_list_url()):
                    with HTTMock(TestGitLabProjectMembersApi().get_mock_for_get_url()):
                        with HTTMock(TestGitLabProjectMemberObjApi().get_mock_for_save_url(args={'access_level': 10})):
                            self.assertTrue(tasks.add_or_update_member(
                                user_id=self.user.id,
                                project_id=1,
                                username='name',
                                access_level=10
                            ))

    @LoginMethods.create_user_wrapper
    @mock_all_gitlab_url
    def test_create_user(self):
        from GitLabApi.tests.test_gitlab_api import TestGitLabProjectsApi, TestGitLabUsersApi, \
            TestGitLabProjectMembersApi

        args_dict = {
            'user_id': self.user.id,
            'access_level': 10,
        }

        with HTTMock(mock_all_urls_and_raise_error):
            with HTTMock(TestGitLabProjectsApi().get_mock_for_get_url()):
                with HTTMock(TestGitLabUsersApi().get_mock_for_list_url()):
                    with HTTMock(TestGitLabProjectMembersApi().get_mock_for_get_url(raise_error=GitlabGetError())):
                        with HTTMock(TestGitLabProjectMembersApi().get_mock_for_create_url(args=args_dict)):
                            self.assertTrue(tasks.add_or_update_member(
                                user_id=self.user.id,
                                project_id=1,
                                username='name',
                                access_level=10
                            ))


class AddMemberTaskTests(LoginMethods):

    @LoginMethods.create_user_wrapper
    def setUp(self):
        self.task_model = AddMemberCreateMethods().create_task(
            owner=GitlabUser.objects.get(user_social_auth=self.user_social_auth)
        )
        self.gitlab_project = self.task_model.gitlab_project

    def get_run_args(self):
        return json.loads(self.task_model.celery_task.kwargs)

    @mock_all_gitlab_url
    def test_gitlab_project_does_not_have_gitlab_id(self):
        self.gitlab_project.gitlab_id = None
        self.gitlab_project.save()

        tasks.AddMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.status, self.task_model.FAILED)
        self.assertNotEqual(self.task_model.error_msg, "")

    @mock_all_gitlab_url
    def test_run_correctly(self):
        self.gitlab_project.gitlab_id = 1
        self.gitlab_project.save()

        tasks.AddMemberTask().run(**self.get_run_args())

        self.task_model.refresh_from_db()
        self.assertEqual(self.task_model.error_msg, None)
        self.assertNotEqual(self.task_model.new_gitlab_user, None)
        self.assertEqual(self.task_model.status, self.task_model.SUCCEED)
