import unittest

from core import exceptions


class FormErrorTests(unittest.TestCase):
    def test_inheritance(self):
        error = exceptions.FormError()
        self.assertIsInstance(error, exceptions.CoreError)

    def test_string_representation(self):
        error_msg = 'error msg'
        error = exceptions.FormError(error_msg)
        self.assertEqual(error.error_msg, error_msg)
        self.assertEqual(str(error), str(error_msg))


class FormNotValidErrorTests(unittest.TestCase):
    def test_inheritance(self):
        error = exceptions.FormNotValidError()
        self.assertIsInstance(error, exceptions.CoreError)

    def test_string_representation(self):
        error_dict = {'error': 'error msg'}
        error = exceptions.FormNotValidError(error_dict)
        self.assertEqual(error.error_dict, error_dict)
        self.assertEqual(str(error), str(error_dict))


class DoesNotContainGitlabIdTests(unittest.TestCase):
    def test_inheritance(self):
        error = exceptions.DoesNotContainGitlabId()
        self.assertIsInstance(error, exceptions.CoreError)

    def test_string_representation(self):
        error_msg = 'error msg'
        error = exceptions.DoesNotContainGitlabId(error_msg)
        self.assertEqual(error.error_msg, error_msg)
        self.assertEqual(str(error), str(error_msg))
