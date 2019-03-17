from SZR.settings.utils import SecretKeyGenerator
from unittest import TestCase, mock


class SecretKeyGeneratorTests(TestCase):
    module_path = SecretKeyGenerator.__module__

    def test_read_from_existing_file(self):
        file_path = 'path'
        file_contain = 'secret_key'
        secret_key_generator = SecretKeyGenerator(file_path)
        with mock.patch('{0}.open'.format(self.module_path), mock.mock_open(read_data=file_contain)) as mock_open:
            key = secret_key_generator.get_or_create()
        self.assertEqual(key, file_contain)
        mock_open.assert_called_once_with(file_path)

    @mock.patch('{0}.open'.format(module_path), return_value=IOError)
    def test_create_not_existing_file_with_key(self, mock_open):
        file_path = 'path'
        mock_open_file = mock.mock_open()
        handlers = (mock_open.return_value, mock_open_file.return_value,)
        mock_open.side_effect = handlers

        key = SecretKeyGenerator(file_path).get_or_create()
        self.assertEqual(len(key), 50)
        self.assertEqual(mock_open.call_count, 2)
        mock_open_file().write.assert_called_once_with(key)

    @mock.patch('{0}.open'.format(module_path), side_effect=[IOError, IOError])
    def test_cannot_create_file(self, mock_open):
        with self.assertRaises(IOError):
            SecretKeyGenerator('path').get_or_create()
            self.assertEqual(mock_open.call_count, 2)
