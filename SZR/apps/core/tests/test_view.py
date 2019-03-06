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
        self.user_social = UserSocialAuth.objects.create(**self.user_social_auth_credentials)

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


# class AdminPageTest(SimpleUrlsTestsCases.SimpleUrlsTests):
#     pattern = '/admin/'
#     app_name = 'admin'
#     name = 'index'
#     login_required = False


class CoreAppNameCase:
    class CoreAppNameTest(SimpleUrlsTestsCases.SimpleUrlsTests):
        app_name = 'core'
        login_required = False


class InitNavbarPageTest(CoreAppNameCase.CoreAppNameTest):
    name = 'init_navbar'

    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/init_navbar.html')


class InitNavbarArgumentsPageTest(CoreAppNameCase.CoreAppNameTest):
    name = 'init_navbar_arguments'
    args = {'arg': '1'}

    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/init_navbar.html')


class InitSidebarPageTest(CoreAppNameCase.CoreAppNameTest):
    name = 'init_sidebar'

    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/init_sidebar.html')


class InitSidebarArgumentsPageTest(CoreAppNameCase.CoreAppNameTest):
    name = 'init_sidebar_arguments'
    args = {'arg': '1'}

    def test_page_found(self):
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/init_sidebar.html')
