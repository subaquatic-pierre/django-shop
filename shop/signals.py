from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ShopProfile


@receiver(signal=post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        ShopProfile.objects.create(user=instance)


@receiver(signal=post_save, sender=User)
def save_user_model(sender, instance, created, **kwargs):
    instance.shopprofile.save()
