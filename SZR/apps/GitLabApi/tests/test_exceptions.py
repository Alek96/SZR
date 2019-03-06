import unittest

from GitLabApi.exceptions import *


class GitlabErrorTests(unittest.TestCase):
    def test_string_representation(self):
        error_message = 'test'
        error = GitlabError(error_message)
        self.assertEqual(error.error_message, error_message)
        self.assertEqual(str(error), error_message)

    def test_string_representation_with_response_code(self):
        error_message = 'test'
        response_code = 400
        error = GitlabError(error_message, response_code)
        self.assertEqual(error.error_message, error_message)
        self.assertEqual(error.response_code, response_code)
        self.assertEqual(str(error), "{0}: {1}".format(response_code, error_message))


class NoMockedUrlErrorTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(NoMockedUrlError(), GitlabError)


class GitlabOperationErrorTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(GitlabOperationError(), GitlabError)

    def test_decode(self):
        gitlab_operation_error = GitlabOperationError("Failed to save group {:path=>[\"has already been taken\"]}")
        self.assertEqual(gitlab_operation_error.decode(), {'path': ['has already been taken']})


class GitlabCreateErrorTests(unittest.TestCase):
    def test_inheritance(self):
        self.assertIsInstance(GitlabCreateError(), GitlabOperationError)

    def test_get_gitlab_create_error_on_group(self):
        self.assertEqual(get_gitlab_create_error_on_group().decode(), {'path': ['has already been taken']})


class WrappersTests(unittest.TestCase):
    def test_on_error(self):
        @on_error(expect_error=GitlabError, raise_error=GitlabOperationError)
        def raise_error():
            raise GitlabError("error")

        with self.assertRaises(GitlabOperationError) as error:
            raise_error()

        self.assertIn('error', str(error.exception))
