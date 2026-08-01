from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_users(sender, **kwargs):
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # 1. Admin account
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@intellihub.ai',
                password='Admin123!',
                role='ADMIN'
            )

        # 2. Demo account
        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(
                username='demo',
                email='demo@intellihub.ai',
                password='Demo123!',
                role='DATA_SCIENTIST'
            )

        # 3. Suraj Vaghela account
        if not User.objects.filter(username='suraj_vaghela').exists():
            User.objects.create_user(
                username='suraj_vaghela',
                email='suraj@intellihub.ai',
                password='Password123!',
                role='DATA_SCIENTIST'
            )
    except Exception as e:
        pass


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'

    def ready(self):
        post_migrate.connect(create_default_users, sender=self)
