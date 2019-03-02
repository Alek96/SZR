import unittest
from django.test import TestCase
from django.urls import reverse

from core.tests.test_view import SimpleUrlsTestsCases, LoginMethods


class RegistrationAppNameCase:
    class RegistrationAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'authentication'
        login_name = 'login'
        logout_name = 'logout'
        login_required = False

        def get_login_view_name(self):
            return '{}:{}'.format(self.app_name, self.login_name)

        def get_logout_view_name(self):
            return '{}:{}'.format(self.app_name, self.logout_name)

        def get_login_url(self):
            return reverse(self.get_login_view_name())

        def get_logout_url(self):
            return reverse(self.get_logout_view_name())


class LoginPageTest(RegistrationAppNameCase.RegistrationAppNameTest):

    @classmethod
    def setUpTestData(cls):
        cls.name = cls.login_name
        super().setUpTestData()

    def test_simple_get_page(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)

    # todo: Erase comment after providing home page ('/')
    def test_login(self):
        self.create_user_to_login()
        response = self.client.post(self.get_login_url(), self.get_user_credentials(), follow=True)

        # self.assertEqual(response.status_code, 200)
        # self.assertRedirects(response, '/')
        # self.assertTrue(response.context['user'].is_authenticated)
        self.assertIn('_auth_user_id', self.client.session)


class LoginGitlabPageTest(RegistrationAppNameCase.RegistrationAppNameTest):
    name = 'login_gitlab'

    def test_simple_get_page(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('social:begin', args=('gitlab',)))


class LogoutPageTest(RegistrationAppNameCase.RegistrationAppNameTest):

    @classmethod
    def setUpTestData(cls):
        cls.name = cls.logout_name
        super().setUpTestData()

    def test_simple_get_page(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.get_login_url())

    @LoginMethods.login_wrapper
    def test_logout(self):
        self.assertIn('_auth_user_id', self.client.session)
        response = self.client.post(self.get_logout_url(), follow=True)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, self.get_login_url())
