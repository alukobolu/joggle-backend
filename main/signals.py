from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()


@receiver(post_save, sender=User)
def create_default_project(sender, instance, created, **kwargs):
    """Create a default 'personal' project for new users"""
    if created:
        Project.objects.create(
            name='Personal',
            description='Your personal tasks and todos',
            color_code='#3B82F6',  # Blue color
            user=instance,
            is_default=True
        )
