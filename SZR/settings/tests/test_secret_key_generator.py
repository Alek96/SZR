from SZR.settings.secret_key_generator import SecretKeyGenerator
from unittest import TestCase, mock


class SecretKeyGeneratorTests(TestCase):
    module_path = 'SZR.settings.secret_key_generator'

    def test_read_from_existing_file(self):
        file_path = 'path'
        file_contain = 'secret_key'
        with mock.patch(self.module_path + '.open', mock.mock_open(read_data=file_contain)) as mock_open:
            key = SecretKeyGenerator(file_path).get_or_create()
        self.assertEqual(key, file_contain)
        mock_open.assert_called_once_with(file_path)

    @mock.patch(module_path + '.open', return_value=IOError)
    def test_create_not_existing_file_with_key(self, mock_open):
        file_path = 'path'
        mock_open_file = mock.mock_open()
        handlers = (mock_open.return_value, mock_open_file.return_value,)
        mock_open.side_effect = handlers

        key = SecretKeyGenerator(file_path).get_or_create()
        self.assertEqual(len(key), 50)
        self.assertEqual(mock_open.call_count, 2)
        mock_open_file().write.assert_called_once_with(key)

    @mock.patch(module_path + '.open', side_effect=[IOError, IOError])
    def test_cannot_create_file(self, mock_open):
        with self.assertRaises(IOError):
            SecretKeyGenerator('path').get_or_create()
            self.assertEqual(mock_open.call_count, 2)
