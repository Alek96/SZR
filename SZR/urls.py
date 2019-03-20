from django.urls import path, include
from django.contrib import admin
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('admin/', admin.site.urls),
    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),

    path('auth/', include('social_django.urls', namespace='social')),
    path('core/', include('core.urls')),
    path('groups/', include('groups.urls')),
]
