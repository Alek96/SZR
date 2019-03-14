import unittest
from django.test import TestCase

from authentication.models import GitlabUser
from core.utils import *


class CapturedOutputTests(unittest.TestCase):
    def test_captured_output_stdout(self):
        with captured_output() as (out, err):
            print("hallo")

        self.assertIn('hallo', out.read())
        self.assertNotIn('hallo', err.read())

    def test_captured_output_stderr(self):
        with captured_output() as (out, err):
            print("hallo", file=sys.stderr)

        self.assertNotIn('hallo', out.read())
        self.assertIn('hallo', err.read())


class PrintSqlTests(TestCase):
    def test_print_sql(self):
        with captured_output() as (out, err):
            print_sql(GitlabUser.objects.create)(gitlab_id=42)

        self.assertIn('INSERT INTO', out.read())

    def test_print_sql_on_error(self):
        @print_sql
        def p():
            GitlabUser.objects.create(gitlab_id=42)
            raise Exception

        with captured_output() as (out, err):
            with self.assertRaises(Exception):
                p()

        self.assertIn('INSERT INTO', out.read())
