from .development import *

# ##### APPLICATION CONFIGURATION #########################

TESTS_APPS = [
    'core.tests.apps.CoreTestConfig',
    'groups.tests.apps.GroupsTestConfig'
]

INSTALLED_APPS = INSTALLED_APPS + TESTS_APPS

MOCK_ALL_GITLAB_URL = True
