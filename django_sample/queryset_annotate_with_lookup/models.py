from django.contrib.auth.models import User
from django.db import models


class TestModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True)
