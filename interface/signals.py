import random
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles import models as profile_models


@receiver(post_save, sender=User)
def add_birdth_date(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.BirthDate.objects.create(user=user)


@receiver(post_save, sender=User)
def add_address(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Address.objects.create(user=user)


@receiver(post_save, sender=User)
def add_auth_code(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.AuthCode.objects.create(user=user)


@receiver(post_save, sender=User)
def add_nickname(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Nickname.objects.create(user=user)


@receiver(post_save, sender=User)
def add_bio(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Bio.objects.create(user=user, content=f'Hi! I am {user.get_full_name()}.')


@receiver(post_save, sender=User)
def add_pics(instance: User, created: bool, *args, **kwargs) -> None:
    user = instance
    if created:
        profile_models.Pic.objects.create(
            user=user,
        )

