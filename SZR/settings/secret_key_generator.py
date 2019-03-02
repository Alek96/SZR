from django.utils.crypto import get_random_string


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
