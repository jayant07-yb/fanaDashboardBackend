from django.core.management.base import BaseCommand
from fanaCallSetup.models import FanaCallRequest

class Command(BaseCommand):
    help = 'Remove duplicate FanaCallRequest entries'

    def handle(self, *args, **kwargs):
        duplicates = FanaCallRequest.objects.values('table_id').annotate(count=models.Count('id')).filter(count__gt=1)
        for duplicate in duplicates:
            table_id = duplicate['table_id']
            entries = FanaCallRequest.objects.filter(table_id=table_id)
            entries.order_by('id')[1:].delete()  # Keep the first entry, delete the rest
        self.stdout.write(self.style.SUCCESS('Successfully removed duplicate entries'))
