from django.db import models

# Create your models here.


class UserModel11(models.Model):
    username = models.CharField(max_length=32)
    password = models.CharField(max_length=24)
    nickname = models.CharField(max_length=255)
    nickname1 = models.CharField(max_length=255, default=None)
    nickname2 = models.CharField(max_length=255, default=None, null=True)
    nickname3 = models.CharField(max_length=255, default=None, null=True)
    nickname4 = models.CharField(max_length=255, default=None, null=True)
    nickname5 = models.CharField(max_length=255, default=None, null=True)