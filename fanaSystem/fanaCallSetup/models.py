from django.db import models

class FanaCallRequest(models.Model):
    REQUEST_TYPES = [
        ('call_waiter', 'Call Waiter'),
        ('bring_bill', 'Bring Bill'),
        ('order', 'Order'),
        ('bring_water', 'Bring Water')
    ]
    
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPES)
    table_id = models.CharField(max_length=20)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.get_request_type_display()} from Table {self.table_id} at {self.timestamp}"
