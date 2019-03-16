from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User as Auth_user
from social_django.models import UserSocialAuth

from core.models import GitlabUser


@receiver(post_save, sender=UserSocialAuth)
def create_gitlab_user(sender, instance, **kwargs):
    def create_user():
        return GitlabUser.objects.create(
            gitlab_id=instance.uid
        )

    def set_social_auth_attributes(gitlab_user):
        gitlab_user.auth_user = auth_user
        gitlab_user.social_auth = instance
        gitlab_user.save()

    if instance.provider != 'gitlab':
        return

    auth_user = Auth_user.objects.get(id=instance.user_id)

    try:
        gitlab_user = GitlabUser.objects.get(gitlab_id=instance.uid)
    except GitlabUser.DoesNotExist:
        gitlab_user = create_user()

    set_social_auth_attributes(gitlab_user)
