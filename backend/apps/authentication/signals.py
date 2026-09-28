from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def seed_default_admin(sender, **kwargs):
    if sender.label != 'authentication':
        return

    user_model = get_user_model()
    if user_model.objects.filter(employee_id='ADMIN').exists():
        return

    user_model.objects.create_superuser(
        employee_id='ADMIN',
        name='ADMIN',
        password='admin1234!',
        role='ADMIN',
        is_staff=True,
        is_superuser=True,
    )