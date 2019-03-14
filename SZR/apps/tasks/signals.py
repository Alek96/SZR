from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask

from tasks.models import *


# @receiver(post_save, sender=AbstractTask)
# def create_task(sender, instance, created, **kwargs):
#     if created:
#         PeriodicTask.objects.created()
#         print("eee")
