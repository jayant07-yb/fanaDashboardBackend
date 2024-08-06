from django.db import models
from django.contrib.auth.models import User

class TableActivity(models.Model):
    table_id = models.IntegerField()
    is_active = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    table = models.ForeignKey('TableActivity', on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
