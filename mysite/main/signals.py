from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        role = 'admin' if instance.is_superuser else 'client'
        Profile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        if instance.is_superuser and instance.profile.role != 'admin':
            instance.profile.role = 'admin'
        instance.profile.save()
