import importlib
from unittest import mock

from django.test import TestCase, override_settings

from SZR.urls import AvailableUrlsMocker


class AvailableUrlsMockerTests(TestCase):
    def test_is_working(self):
        mocker = AvailableUrlsMocker()
        self.assertNotEqual(mocker._get_urlpatterns_list(), [])

    @override_settings(PROJECT_APPS=[])
    def test_return_empty_list_if_PROJECT_APPS_is_empty(self):
        mocker = AvailableUrlsMocker()
        self.assertEqual(mocker._get_urlpatterns_list(), [])

    @override_settings(PROJECT_APPS=['aaa'])
    def test_return_empty_list_if_PROJECT_APPS_does_not_have_urls_modules(self):
        mocker = AvailableUrlsMocker()
        self.assertEqual(mocker._get_urlpatterns_list(), [])

    @override_settings(PROJECT_APPS=['SZR'])
    def test_return_empty_list_if_PROJECT_APPS_has_empty_urlpatterns(self):
        mocker = AvailableUrlsMocker()
        with mock.patch('{0}.locate'.format(mocker.__module__), return_value=[]) as mock_locate:
            self.assertEqual(mocker._get_urlpatterns_list(), [])
        mock_locate.assert_called_once_with('SZR.urls.urlpatterns')

    @override_settings(PROJECT_APPS=['aaa'])
    def test_return_empty_list_if_PROJECT_APPS_has_empty_urlpatterns(self):
        mocker = AvailableUrlsMocker()
        with mock.patch('{0}.locate'.format(mocker.__module__), side_effect=AttributeError) as mock_locate:
            self.assertEqual(mocker._get_urlpatterns_list(), [])
        mock_locate.assert_called_once_with('aaa.urls.urlpatterns')
