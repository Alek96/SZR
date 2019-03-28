import unittest
from django.test import TestCase
from django.urls import reverse, resolve
from django.conf import settings
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
import functools


class UserCredentials:
    user_credentials = {
        'username': 'userTest',
        'email': 'email@example.com',
        'password': 'password',
    }

    user_social_auth_credentials = {
        'provider': 'gitlab',
        'uid': 500,
        'user_id': 1,
        'extra_data': {
            "auth_time": 0,
            "id": 500,
            "expires": None,
            "refresh_token": "aaa",
            "access_token": "bbb",
            "token_type": "bearer"}
    }

    def get_user_credentials(self):
        return {
            'username': self.user_credentials['username'],
            'password': self.user_credentials['password'],
        }


class LoginMethods(TestCase, UserCredentials):

    def create_user_to_login(self):
        self.user = User.objects.create_user(**self.user_credentials)
        self.user_social_auth = UserSocialAuth.objects.create(**self.user_social_auth_credentials)

    def create_user_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.create_user_to_login()
            return func(self, *args, **kwargs)

        return wrapper

    def login(self):
        self.create_user_to_login()
        return self.client.login(**self.get_user_credentials())

    def logout(self):
        return self.client.logout()

    def login_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.login()
            return func(self, *args, **kwargs)

        return wrapper

    def logout_wrapper(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            self.logout()
            return func(self, *args, **kwargs)

        return wrapper


class SimpleUrlsTestsCases:
    class SimpleUrlsTests(LoginMethods):
        pattern = None
        app_name = ''
        name = ''
        args = None
        status_code = 0
        login_required = True

        def get_view_name(self):
            return self.app_name + ':' + self.name if self.app_name else self.name

        def get_url(self):
            return reverse(self.get_view_name(), kwargs=self.args)

        def test_get_url_from_name(self):
            url = self.get_url()
            if self.pattern:
                self.assertEqual(url, self.pattern)

        def test_get_view(self):
            resolver = resolve(self.get_url())
            self.assertEqual(resolver.view_name, self.get_view_name())

        def test_get_page(self):
            self.client.get(self.get_url())

        def test_call_view_denies_anonymous(self):
            if not self.login_required:
                self.skipTest("Require protected view")
            response = self.client.get(self.get_url(), follow=True)
            self.assertContains(response, reverse(settings.LOGIN_URL))
            response = self.client.post(self.get_url(), follow=True)
            self.assertContains(response, reverse(settings.LOGIN_URL))


class RegistrationAppNameCase:
    class RegistrationAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'core'
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

    def test_login(self):
        self.create_user_to_login()
        response = self.client.post(self.get_login_url(), self.get_user_credentials(), follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, '/')
        self.assertTrue(response.context['user'].is_authenticated)
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
