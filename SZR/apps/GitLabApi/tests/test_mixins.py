import unittest
from unittest import mock

from GitLabApi import base
from GitLabApi.mixins import *


class FakeGitlab(object):
    foo = 'bar'


class FakeObject(base.RESTObject):
    _attrs = ['foo', 'args']


class FakeManager(base.RESTManager):
    _obj_cls = FakeObject


# @unittest.skip
# class TestObjectMixinsAttributes(unittest.TestCase):
#     def test_access_request_mixin(self):
#         class O(AccessRequestMixin):
#             pass
#
#         obj = O()
#         self.assertTrue(hasattr(obj, 'approve'))


class TestMetaMixins(unittest.TestCase):
    def test_crud_mixin(self):
        class M(CRUDMixin):
            pass

        obj = M(FakeGitlab())
        self.assertTrue(hasattr(obj, 'get'))
        self.assertTrue(hasattr(obj, 'list'))
        self.assertTrue(hasattr(obj, 'create'))
        self.assertTrue(hasattr(obj, 'update'))
        self.assertTrue(hasattr(obj, 'delete'))
        self.assertIsInstance(obj, ListMixin)
        self.assertIsInstance(obj, GetMixin)
        self.assertIsInstance(obj, CreateMixin)
        self.assertIsInstance(obj, UpdateMixin)
        self.assertIsInstance(obj, DeleteMixin)


class TestMixinMethods(unittest.TestCase):
    def test_get_mixin(self):
        class M(GetMixin, FakeManager):
            pass

        class FakeGet(FakeGitlab):
            def get(self, *args, **kwargs):
                self.args = args
                return FakeGitlab()

        mgr = M(FakeGet())
        obj = mgr.get(42)
        self.assertIsInstance(obj, FakeObject)
        self.assertIsInstance(obj._rest_object, FakeGitlab)
        self.assertEqual(obj.foo, 'bar')
        self.assertEqual(mgr._rest_manager.args, (42,))

    def test_list_mixin(self):
        class M(ListMixin, FakeManager):
            pass

        class FakeList(FakeGitlab):
            def list(self, **kwargs):
                return [FakeGitlab, FakeGitlab]

        mgr = M(FakeList())
        obj_list = mgr.list()
        self.assertIsInstance(obj_list, list)
        self.assertIsInstance(obj_list[0], FakeObject)
        self.assertEqual(len(obj_list), 2)

    def test_create_mixin(self):
        class M(CreateMixin, FakeManager):
            pass

        class FakeCreate(FakeGitlab):
            def create(self, *args, **kwargs):
                self.args = args
                return FakeGitlab()

        mgr = M(FakeCreate())
        obj = mgr.create({'foo': 'bar'})
        self.assertIsInstance(obj, FakeObject)
        self.assertEqual(mgr._rest_manager.args, ({'foo': 'bar'},))

    def test_update_mixin(self):
        class M(UpdateMixin, FakeManager):
            pass

        class FakeUpdate(FakeGitlab):
            def update(self, *args, **kwargs):
                self.args = args

        mgr = M(FakeUpdate())
        mgr.update(42, {'foo': 'bar'})
        self.assertEqual(mgr._rest_manager.args, (42, {'foo': 'bar'}))

    @unittest.skip
    def test_delete_mixin(self):
        class M(DeleteMixin, FakeManager):
            pass

        class FakeDelete(FakeGitlab):
            def delete(self, *args, **kwargs):
                self.args = args

        mgr = M(FakeDelete())
        mgr.delete(42)
        self.assertEqual(mgr._rest_manager.args, (42,))
