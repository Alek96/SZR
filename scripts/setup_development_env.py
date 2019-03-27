from django.contrib.auth.models import User

User.objects.filter(username='django', email='admin@example.com').delete()
User.objects.create_superuser(username='django', email='admin@example.com', password='django')
