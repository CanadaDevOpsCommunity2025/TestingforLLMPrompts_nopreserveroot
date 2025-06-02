from django.db import models
from django.contrib.auth.models import AbstractBaseUser


class prompt(models.Model):
    name = models.CharField(unique=True)

    def __str__(self):
        return str(self.name)
