# Python imports
from .utils import SecretKeyGenerator
from os.path import abspath, basename, dirname, join, normpath
import sys

# local configurations
from .my_social_keys import *

# ##### PATH CONFIGURATION ################################

# fetch Django's project directory
DJANGO_ROOT = dirname(dirname(abspath(__file__)))

# fetch the project_root
PROJECT_ROOT = dirname(DJANGO_ROOT)

# the name of the whole site
SITE_NAME = basename(DJANGO_ROOT)

# temporary files here
TMP_PATH = abspath(join(PROJECT_ROOT, 'tmp'))

# collect static files here
STATIC_ROOT = join(PROJECT_ROOT, TMP_PATH, 'static')

# collect media files here
MEDIA_ROOT = join(PROJECT_ROOT, TMP_PATH, 'media')

# look for static assets here
STATICFILES_DIRS = [
    join(PROJECT_ROOT, 'static'),
]

# look for templates here
# This is an internal setting, used in the TEMPLATES directive
PROJECT_TEMPLATES = [
    join(PROJECT_ROOT, 'templates'),
]

# add project_name/apps/ to the Python path
sys.path.append(normpath(join(PROJECT_ROOT, 'SZR/apps')))

# ##### APPLICATION CONFIGURATION #########################

# Apps
PREREQUISITE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'social_django',
    'django_celery_results',
    'django_celery_beat',
]

PROJECT_APPS = [
    'core.apps.CoreConfig',
    'groups.apps.GroupsConfig',
]

DEFAULT_APPS = PREREQUISITE_APPS + PROJECT_APPS

# Middlewares
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.gitlab.GitLabOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)

# template stuff
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': PROJECT_TEMPLATES,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

# Internationalization
USE_I18N = False

# ##### SECURITY CONFIGURATION ############################

# We store the secret key here
# The required SECRET_KEY is fetched at the end of this file
SECRET_FILE = normpath(join(PROJECT_ROOT, TMP_PATH, 'SECRET.key'))

# these persons receive error notification
ADMINS = (
    ('your name', 'your_name@example.com'),
)
MANAGERS = ADMINS

# ##### DJANGO RUNNING CONFIGURATION ######################

# the default WSGI application
WSGI_APPLICATION = '%s.wsgi.application' % SITE_NAME

# the root URL configuration
ROOT_URLCONF = '%s.urls' % SITE_NAME

# the URL for static files
STATIC_URL = '/static/'

# the URL for media files
MEDIA_URL = '/media/'

# finally grab the SECRET KEY
SECRET_KEY = SecretKeyGenerator(SECRET_FILE).get_or_create()

# adjust the minimal login
LOGIN_URL = 'core:login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'core:login'

# ##### CELERY CONFIGURATION ###############################
CELERY_RESULT_BACKEND = 'django-db'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# ##### DEBUG CONFIGURATION ###############################
DEBUG = False

# Run Celery synchronously
TEST_RUNNER = "SZR.settings.utils.CeleryTestSuiteRunner"
