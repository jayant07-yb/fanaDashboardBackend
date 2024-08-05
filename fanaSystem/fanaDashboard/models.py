from django.db import models
from django.utils import timezone

from django.contrib.auth.models import User

class FanaCallRequest(models.Model):
    TABLE_STATES = [
        ('pressed', 'Pressed'),
        ('not_pressed', 'Not Pressed'),
        ('in_progress', 'In Progress')
    ]

    table_id = models.CharField(max_length=20, unique=True)
    call_waiter_state = models.CharField(max_length=20, choices=TABLE_STATES, default='not_pressed')
    bring_bill_state = models.CharField(max_length=20, choices=TABLE_STATES, default='not_pressed')
    order_state = models.CharField(max_length=20, choices=TABLE_STATES, default='not_pressed')
    bring_water_state = models.CharField(max_length=20, choices=TABLE_STATES, default='not_pressed')
    timestamp = models.DateTimeField(default=timezone.now)
    handled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Table {self.table_id} at {self.timestamp}"
