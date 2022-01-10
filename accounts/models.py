from django.db import models
from django.db.models.deletion import CASCADE
from django.contrib.auth.models import (PermissionsMixin, BaseUserManager, AbstractBaseUser )
from django.db.models.query import QuerySet
# from .utils import Util


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

    username=models.CharField(max_length=200, unique=True, db_index=True)
    email=models.EmailField(max_length=100, unique=True, db_index=True)
    fullname = models.CharField(max_length= 100, default=None, null=True)
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

class Currency(models.Model):
    currency_types = [
        ('USD', 'USD'),
        ('GBP', 'GBP'),
        ('EUR', 'EUR'),
        ('NGN', 'NGN'),
    ]
    currency_category = models.CharField(max_length=15, default=0, choices=currency_types)

    def __str__(self):
        return self.currency_category

class User_type(models.Model):
    user_types = [
        ('Noobs', 'Noobs'),
        ('Elite', 'Elite'),
    ]
    users = models.CharField(max_length=15, default=0, choices=user_types)

    def __str__(self):
        return self.users

class UserAccountSettings(models.Model):
    user_id = models.ForeignKey(User, default=0, on_delete=CASCADE)
    currency_types = models.ForeignKey(Currency, default=0, on_delete=CASCADE)
    user_types = models.ForeignKey(User_type, default=None, on_delete=CASCADE, null=True)
    wallet_id = models.CharField(max_length=15, unique=True, primary_key=True)

    def generate_key(self):
        wallet_id = Util.generate_wallet_id()

        if UserAccountSettings.objects.filter(wallet_address=wallet_id).exists():
            return self.generate_key()

        return wallet_id

    def save(self, *args, **kwargs):
        if not self.wallet_address:
            self.wallet_address = self.generate_key()

        return super(UserAccountSettings, self).save(*args, **kwargs)

    def __str__(self):
        return self.wallet_address


class eWallet(models.Model):
    user_id = models.ForeignKey(User, default=0, null=True, on_delete=CASCADE)
    currency_type = models.ForeignKey(Currency, default=0, null=True, on_delete=CASCADE)
    balance = models.DecimalField(max_digits=100, decimal_places=2)
    wallet_id = models.ForeignKey(UserAccountSettings, default=0, on_delete=CASCADE)

class Fund_eWallet(models.Model):
    user_id = models.ForeignKey(User, default=0, null=True, on_delete=CASCADE)
    wallet_id = models.ForeignKey(UserAccountSettings, default=0, on_delete=CASCADE)
    currency_type = models.ForeignKey(Currency, default=0, null=True, on_delete=CASCADE)
    amount = models.DecimalField(max_digits=50, decimal_places=2, null=True)

class Withdrawal(models.Model):
    user_id = models.ForeignKey(User, default = 0, on_delete=CASCADE)
    currency_types = models.ForeignKey(Currency, default = 0, on_delete=CASCADE)
    wallet_address = models.ForeignKey(eWallet, default = 0, on_delete=CASCADE)
    wallet_id = models.CharField(max_length=50, default= None)
    amount = models.CharField(max_length=50, default=None)
    user_types = models.ForeignKey(User_type, default = 0, on_delete=CASCADE)
    status = models.CharField(max_length=50, default=None)





