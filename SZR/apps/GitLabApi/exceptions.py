import functools
import json


class GitlabError(Exception):
    def __init__(self, error_message="", response_code=None, response_body=None):
        super().__init__(error_message)
        self.error_message = error_message
        self.response_code = response_code
        self.response_body = response_body

    def __str__(self):
        if self.response_code is not None:
            return "{0}: {1}".format(self.response_code, self.error_message)
        else:
            return "{0}".format(self.error_message)


class NoMockedUrlError(GitlabError):
    pass


class GitlabOperationError(GitlabError):

    def decode(self):
        dict_str = self.error_message[self.error_message.index('{'):]
        dict_str = dict_str.replace(":", '"')
        dict_str = dict_str.replace("=>", '" : ')
        dict_str = dict_str.replace('""', '"')
        return json.loads(dict_str)


class GitlabCreateError(GitlabOperationError):
    pass


def get_gitlab_create_error_on_group():
    return GitlabCreateError("Failed to save group {:path=>[\"has already been taken\"]}")


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
