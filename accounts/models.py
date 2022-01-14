from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import (PermissionsMixin, BaseUserManager, AbstractBaseUser )
from django.db.models.query import QuerySet
from rest_framework import serializers
from .utils import Util


# Create your models here.
class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError('User should enter a username')
        if email is None:
            raise TypeError('User should enter an Email')

        user=self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):
        if password is None:
            raise TypeError('Password must be entered')

        user=self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user

class User(AbstractBaseUser,PermissionsMixin):
    user_types = [
        ('Noob', 'Noob'),
        ('Elite', 'Elite'),
        ('Admin', 'Admin'),
    ]
    types = models.CharField(max_length=15, default="Noob", choices=user_types)
    username=models.CharField(max_length=200, unique=True, db_index=True)
    email=models.EmailField(max_length=100, unique=True, db_index=True)
    is_verified=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return self.email


class Ewallet(models.Model):
    currency_types = [
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
        ('NGN', 'NGN'),
    ]
    user_id = models.ForeignKey(User, default=0, null=True, on_delete=CASCADE)
    currency = models.CharField(max_length=15, default=0, choices=currency_types)
    balance = models.DecimalField(max_digits=100, decimal_places=2)

    def __str__(self):
        return self.currency
