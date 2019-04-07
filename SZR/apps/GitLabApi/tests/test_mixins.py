import unittest

from GitLabApi import base
from GitLabApi import exceptions
from GitLabApi import mixins
from gitlab import exceptions as gl_exceptions


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
        class M(mixins.CRUDMixin):
            pass

        obj = M(FakeGitlab())
        self.assertTrue(hasattr(obj, 'get'))
        self.assertTrue(hasattr(obj, 'list'))
        self.assertTrue(hasattr(obj, 'create'))
        self.assertTrue(hasattr(obj, 'update'))
        self.assertTrue(hasattr(obj, 'delete'))
        self.assertIsInstance(obj, mixins.ListMixin)
        self.assertIsInstance(obj, mixins.GetMixin)
        self.assertIsInstance(obj, mixins.CreateMixin)
        self.assertIsInstance(obj, mixins.UpdateMixin)
        self.assertIsInstance(obj, mixins.DeleteMixin)


class TestMixinMethods(unittest.TestCase):
    def test_get_mixin(self):
        class M(mixins.GetMixin, FakeManager):
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

    def test_get_mixin_err(self):
        class M(mixins.GetMixin, FakeManager):
            pass

        class FakeGet(FakeGitlab):
            def get(self, *args, **kwargs):
                raise gl_exceptions.GitlabGetError('error')

        with self.assertRaises(exceptions.GitlabGetError) as error:
            M(FakeGet()).get(42)
        self.assertIn('error', str(error.exception))

    def test_list_mixin(self):
        class M(mixins.ListMixin, FakeManager):
            pass

        class FakeList(FakeGitlab):
            def list(self, **kwargs):
                return [FakeGitlab, FakeGitlab]

        mgr = M(FakeList())
        obj_list = mgr.list()
        self.assertIsInstance(obj_list, list)
        self.assertIsInstance(obj_list[0], FakeObject)
        self.assertEqual(len(obj_list), 2)

    def test_list_mixin_err(self):
        class M(mixins.ListMixin, FakeManager):
            pass

        class FakeList(FakeGitlab):
            def list(self, **kwargs):
                raise gl_exceptions.GitlabListError('error')

        with self.assertRaises(exceptions.GitlabListError) as error:
            M(FakeList()).list()
        self.assertIn('error', str(error.exception))

    def test_create_mixin(self):
        class M(mixins.CreateMixin, FakeManager):
            pass

        class FakeCreate(FakeGitlab):
            def create(self, *args, **kwargs):
                self.args = args
                return FakeGitlab()

        mgr = M(FakeCreate())
        obj = mgr.create({'foo': 'bar'})
        self.assertIsInstance(obj, FakeObject)
        self.assertEqual(mgr._rest_manager.args, ({'foo': 'bar'},))

    def test_create_mixin_err(self):
        class M(mixins.CreateMixin, FakeManager):
            pass

        class FakeCreate(FakeGitlab):
            def create(self, *args, **kwargs):
                raise gl_exceptions.GitlabCreateError('error')

        with self.assertRaises(exceptions.GitlabCreateError) as error:
            M(FakeCreate()).create({})
        self.assertIn('error', str(error.exception))

    def test_update_mixin(self):
        class M(mixins.UpdateMixin, FakeManager):
            pass

        class FakeUpdate(FakeGitlab):
            def update(self, *args, **kwargs):
                self.args = args

        mgr = M(FakeUpdate())
        mgr.update(42, {'foo': 'bar'})
        self.assertEqual(mgr._rest_manager.args, (42, {'foo': 'bar'}))

    def test_update_mixin_err(self):
        class M(mixins.UpdateMixin, FakeManager):
            pass

        class FakeUpdate(FakeGitlab):
            def update(self, *args, **kwargs):
                raise gl_exceptions.GitlabUpdateError('error')

        with self.assertRaises(exceptions.GitlabUpdateError) as error:
            M(FakeUpdate()).update(42, {'foo': 'bar'})
        self.assertIn('error', str(error.exception))

    def test_delete_mixin(self):
        class M(mixins.DeleteMixin, FakeManager):
            pass

        class FakeDelete(FakeGitlab):
            def delete(self, *args, **kwargs):
                self.args = args

        mgr = M(FakeDelete())
        mgr.delete(42)
        self.assertEqual(mgr._rest_manager.args, (42,))

    def test_delete_mixin_err(self):
        class M(mixins.DeleteMixin, FakeManager):
            pass

        class FakeDelete(FakeGitlab):
            def delete(self, *args, **kwargs):
                raise gl_exceptions.GitlabDeleteError('error')

        with self.assertRaises(exceptions.GitlabDeleteError) as error:
            M(FakeDelete()).delete(42)
        self.assertIn('error', str(error.exception))

    @unittest.skip('We test it in test_gitlab_api with real Gitlab')
    def test_all_mixin(self):
        class M(mixins.AllMixin, FakeManager):
            pass

        class FakeAll(FakeGitlab):
            def all(self, **kwargs):
                return [FakeGitlab, FakeGitlab]

        mgr = M(FakeAll())
        obj_list = mgr.all()
        self.assertIsInstance(obj_list, list)
        self.assertIsInstance(obj_list[0], FakeObject)
        self.assertEqual(len(obj_list), 2)

    def test_all_mixin_err(self):
        class M(mixins.AllMixin, FakeManager):
            pass

        class FakeAll(FakeGitlab):
            def all(self, **kwargs):
                raise gl_exceptions.GitlabListError('error')

        with self.assertRaises(exceptions.GitlabListError) as error:
            M(FakeAll()).all()
        self.assertIn('error', str(error.exception))
