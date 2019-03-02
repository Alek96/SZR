from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),

    path('auth/', include('social_django.urls', namespace='social')),
    path('core/', include('core.urls')),
    path('authentication/', include('authentication.urls')),
    path('groups/', include('groups.urls')),
]
