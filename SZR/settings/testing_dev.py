from .development import *

# ##### APPLICATION CONFIGURATION #########################

# Apps for testing
TESTS_APPS = [
    'core.tests.apps.CoreTestConfig',
    'groups.tests.apps.GroupsTestConfig'
]

INSTALLED_APPS = INSTALLED_APPS + TESTS_APPS

# Weaker password hasher for faster tests running
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

MOCK_ALL_GITLAB_URL = True
