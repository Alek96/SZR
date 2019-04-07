class CoreError(Exception):
    pass


class FormError(CoreError):
    def __init__(self, error_msg=''):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg


class FormNotValidError(FormError):
    def __init__(self, error_dict={}):
        super().__init__(str(error_dict))
        self.error_dict = error_dict
        self.error_msg = str(self.error_dict)


class DoesNotContainGitlabId(CoreError):
    def __init__(self, error_msg=''):
        self.error_msg = error_msg

    def __str__(self):
        return self.error_msg
