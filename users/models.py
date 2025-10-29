from django.contrib.auth.models import AbstractUser
from django.db import models

class Users(AbstractUser):
    is_customer = models.BooleanField(default=True)
    is_vendor = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    account_id = models.IntegerField(null=True)
    account_name = models.CharField(max_length=100, null=True)
    account_password = models.CharField(max_length=100, null=True)
    phone_number = models.CharField(max_length=100, null=True)
