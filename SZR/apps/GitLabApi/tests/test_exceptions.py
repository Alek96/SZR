import unittest

from GitLabApi.exceptions import *


class GitlabErrorTests(unittest.TestCase):
    def test_init_normal_error_message(self):
        error_message = 'test'
        error = GitlabError(error_message)
        self.assertEqual(error.error_message, error_message)

    def test_init_ruby_error_message(self):
        error_message = 'Failed to save group {:path=>[\"has already been taken\"]}'
        error = GitlabError(error_message)
        self.assertNotEqual(error.error_message, error_message)
        self.assertEqual(error.get_error_dict(), {'path': ['has already been taken']})

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


class WrappersTests(unittest.TestCase):
    def test_on_error(self):
        @on_error(expect_error=GitlabError, raise_error=GitlabOperationError)
        def raise_error():
            raise GitlabError("error")

        with self.assertRaises(GitlabOperationError) as error:
            raise_error()

        self.assertIn('error', str(error.exception))
