import random

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    default_start_address = models.CharField(max_length=255, null=True, blank=True)