from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

uid = 0
user = User.objects.get(username='django', email='admin@example.com')
UserSocialAuth.objects.filter(provider='gitlab', uid=uid).delete()
UserSocialAuth.objects.create(
    provider='gitlab',
    uid=uid,
    user_id=user.id,
    extra_data={
        "auth_time": 0,
        "id": uid,
        "expires": None,
        "refresh_token": "aaa",
        "access_token": "bbb",
        "token_type": "bearer"
    }
)
