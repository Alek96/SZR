class WrongFormError(Exception):
    def __init__(self, error_dict={}):
        super().__init__(str(error_dict))
        self.error_dict = error_dict

    def __str__(self):
        return str(self.error_dict)
