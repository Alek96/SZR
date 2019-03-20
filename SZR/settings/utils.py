from django.utils.crypto import get_random_string
from django.conf import settings
from django.test.runner import DiscoverRunner
from celery import current_app

import logging


class SecretKeyGenerator:
    def __init__(self, secret_file_path):
        self.secret_file_path = secret_file_path

    def get_or_create(self):
        try:
            secret_key = open(self.secret_file_path).read().strip()
        except IOError:
            secret_key = self._generate_key()
            self._write_to_file(secret_key)
        return secret_key

    @staticmethod
    def _generate_key():
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!$%&()=+-_'
        secret_key = get_random_string(50, chars)
        return secret_key

    def _write_to_file(self, text):
        try:
            with open(self.secret_file_path, 'w') as f:
                f.write(text)
        except IOError:
            raise IOError('Could not open %s for writing!' % self.secret_file_path)


# https://github.com/celery/django-celery/blob/master/djcelery/contrib/test_runner.py

USAGE = """\
Custom test runner to allow testing of celery delayed tasks.
"""


def _set_eager():
    settings.CELERY_ALWAYS_EAGER = True
    current_app.conf.CELERY_ALWAYS_EAGER = True
    settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True  # Issue #75
    current_app.conf.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class CeleryTestSuiteRunner(DiscoverRunner):
    """Django test runner allowing testing of celery delayed tasks.
    All tasks are run locally, not in a worker.
    To use this runner set ``settings.TEST_RUNNER``::
        TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'
    """

    def setup_test_environment(self, **kwargs):
        _set_eager()
        super().setup_test_environment(**kwargs)

    def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # Don't show logging messages while testing
        logging.disable(logging.CRITICAL)

        return super().run_tests(test_labels, extra_tests, **kwargs)
