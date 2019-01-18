from django.db import models

from django.contrib.auth.models import AbstractUser


class Profile(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', verbose_name='Avatar',
                               null=True, blank=True)
    AbstractUser._meta.get_field('username').verbose_name = 'Login'
    AbstractUser._meta.get_field('email').verbose_name = 'Emai'
