from django.test import TestCase

from SZR.celery import debug_task
from core.utils import captured_output


class CeleryTest(TestCase):
    def test_debug_task(self):
        with captured_output() as (out, err):
            result = debug_task.delay()

        self.assertIn(result.id, out.read())
        self.assertTrue(result.successful())
