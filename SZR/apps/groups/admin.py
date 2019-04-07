from django.contrib import admin

from . import models

admin.site.register(models.GitlabGroup)
admin.site.register(models.AddSubgroupGroup)
admin.site.register(models.AddSubgroup)
admin.site.register(models.AddMemberGroup)
admin.site.register(models.AddMember)
