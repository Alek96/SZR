# Python imports
from os.path import join

# project imports
from .common import *

# uncomment the following line to include i18n
from .i18n import *

# ##### DEBUG CONFIGURATION ###############################
DEBUG = True

# allow all hosts during development
ALLOWED_HOSTS = ['*']

# ##### DATABASE CONFIGURATION ############################
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_ROOT, TMP_PATH, 'dev.sqlite3'),
    }
}

# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS

SITE_ID = 1

# GITLAB
SOCIAL_AUTH_GITLAB_SCOPE = ['api']

# FRONTEND DEVELOPMENT DEFAULT VALUES
MOCK_ALL_GITLAB_URL = False
