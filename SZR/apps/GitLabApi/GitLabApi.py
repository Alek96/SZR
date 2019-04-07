import gitlab
from GitLabApi.objects import GroupManager, UserManager, ProjectManager
from django.conf import settings


class GitLabApi:
    def __init__(self, user_id):
        self._gitlab = self._get_gitlab_connection(user_id)

        self.groups = GroupManager(self._gitlab.groups)
        self.users = UserManager(self._gitlab.users)
        self.projects = ProjectManager(self._gitlab.projects)

    def _get_gitlab_connection(self, user_id):
        from core.models import GitlabUser

        gitlab_user = GitlabUser.objects.get(user_id=user_id)
        return gitlab.Gitlab(settings.SOCIAL_AUTH_GITLAB_API_URL, oauth_token=gitlab_user.get_access_token())
