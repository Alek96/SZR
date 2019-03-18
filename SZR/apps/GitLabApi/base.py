class RESTObject(object):
    def __init__(self, rest_object):
        self.__dict__.update({
            '_rest_object': rest_object
        })

    def __getattr__(self, name):
        return getattr(self._rest_object, name)

    def __setattr__(self, name, value):
        setattr(self._rest_object, name, value)

    def __dir__(self):
        ret = super().__dir__()
        ret.extend([str(k) for k in self._rest_object.attributes.keys()])
        ret.sort()
        return ret


class RESTManager:
    _obj_cls = None

    def __init__(self, rest_manager):
        self._rest_manager = rest_manager
