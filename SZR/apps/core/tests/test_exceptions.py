import unittest

from core.exceptions import *


class WrongFormErrorTests(unittest.TestCase):
    def test_string_representation(self):
        error_dict = {'error': 'error msg'}
        error = WrongFormError(error_dict)
        self.assertEqual(error.error_dict, error_dict)
        self.assertEqual(str(error), str(error_dict))
