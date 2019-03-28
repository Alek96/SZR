import functools
import json

NON_FIELD_ERRORS = '__all__'


class GitlabError(Exception):
    def __init__(self, error_message="", response_code=None, response_body=None):
        super().__init__(error_message)
        if "=>" in error_message:
            self.error_message = self._decode_from_ruby_dict(error_message)
        else:
            self.error_message = error_message

        self.response_code = response_code
        self.response_body = response_body

    def __str__(self):
        if self.response_code is not None:
            return "{0}: {1}".format(self.response_code, self.error_message)
        else:
            return "{0}".format(self.error_message)

    def _decode_from_ruby_dict(self, ruby_dict):
        dict_str = ruby_dict.replace(":", '"')
        dict_str = dict_str.replace("=>", '" : ')
        dict_str = dict_str.replace('""', '"')
        return dict_str

    def get_error_dict(self):
        try:
            dict_str = self.error_message[self.error_message.index('{'):]
            return json.loads(dict_str)
        except ValueError:
            return {NON_FIELD_ERRORS: [self.error_message]}


class NoMockedUrlError(GitlabError):
    pass


class GitlabOperationError(GitlabError):
    pass


class GitlabListError(GitlabOperationError):
    pass


class GitlabGetError(GitlabOperationError):
    pass


class GitlabCreateError(GitlabOperationError):
    pass


class GitlabUpdateError(GitlabOperationError):
    pass


class GitlabDeleteError(GitlabOperationError):
    pass


def on_error(expect_error, raise_error):
    def wrap(f):
        @functools.wraps(f)
        def wrapped_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except expect_error as e:
                raise raise_error(e.error_message, e.response_code, e.response_body)

        return wrapped_f

    return wrap
