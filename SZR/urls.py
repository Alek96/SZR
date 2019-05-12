from django.urls import path, include
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog
from django.conf import settings
from pydoc import locate

from core.views import home
from GitLabApi import mock_all_gitlab_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('auth/', include('social_django.urls', namespace='social')),
    path('core/', include('core.urls')),
    path('groups/', include('groups.urls')),
    path('projects/', include('projects.urls')),
    path('', home, name='home')
]


class AvailableUrlsMocker:
    def _get_urlpatterns_list(self):
        urlpatterns_list = []
        for app in settings.PROJECT_APPS:
            try:
                _urlpatterns = locate('{0}.urls.urlpatterns'.format(app))
            except:
                continue
            if _urlpatterns:
                urlpatterns_list.append(_urlpatterns)
        return urlpatterns_list

    def mock(self):
        urlpatterns_list = self._get_urlpatterns_list()
        for urlpatterns in urlpatterns_list:
            for urlpattern in urlpatterns:
                urlpattern.callback = mock_all_gitlab_url(urlpattern.callback)


if settings.MOCK_ALL_GITLAB_URL:
    AvailableUrlsMocker().mock()
