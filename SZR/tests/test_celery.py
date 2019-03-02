import sys
from contextlib import contextmanager
from io import StringIO
from django.test import TestCase

from SZR.celery import debug_task


@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
        sys.stdout.seek(0)
        sys.stderr.seek(0)
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class CeleryTest(TestCase):
    def test_1(self):
        with captured_output() as (out, err):
            result = debug_task.delay()

        self.assertIn(result.id, out.read())
        self.assertTrue(result.successful())
