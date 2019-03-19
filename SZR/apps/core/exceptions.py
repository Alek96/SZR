class CoreError(Exception):
    pass


class WrongFormError(CoreError):
    def __init__(self, error_dict={}):
        super().__init__(str(error_dict))
        self.error_dict = error_dict

    def __str__(self):
        return str(self.error_dict)


class DoesNotContainGitlabId(CoreError):
    def __init__(self, error_msg=''):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg
