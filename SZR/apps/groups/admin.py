from django.contrib import admin

from .models import *

admin.site.register(GitlabGroup)
admin.site.register(AddMemberGroup)
admin.site.register(AddMember)
