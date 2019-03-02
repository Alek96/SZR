import unittest

from GitLabApi import base


class FakeGitlab(object):
    foo = 'bar'

    @property
    def attributes(self):
        return {'foo': 'bar'}


class FakeObject(base.RESTObject):
    pass


class FakeManager(base.RESTManager):
    _obj_cls = FakeObject


class TestRESTManager(unittest.TestCase):
    def test_instance(self):
        class MGR(base.RESTManager):
            _obj_cls = FakeObject

        mgr = MGR(FakeGitlab())
        self.assertIsInstance(mgr._rest_manager, FakeGitlab)


class TestRESTObject(unittest.TestCase):
    def test_instance(self):
        obj = FakeObject(FakeGitlab())
        self.assertIsInstance(obj._rest_object, FakeGitlab)

    def test_attrs_get(self):
        obj = FakeObject(FakeGitlab())

        self.assertEqual('bar', obj.foo)
        self.assertRaises(AttributeError, getattr, obj, 'bar')

    def test_attrs_set(self):
        obj = FakeObject(FakeGitlab())

        obj.foo = 'baz'
        self.assertEqual('baz', obj.foo)

    def test_dir(self):
        obj = FakeObject(FakeGitlab())

        self.assertIn('foo', obj.__dir__())
