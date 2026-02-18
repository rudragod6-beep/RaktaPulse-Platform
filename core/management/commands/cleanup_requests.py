from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import BloodRequest
from datetime import timedelta

class Command(BaseCommand):
    help = 'Deletes old blood requests based on urgency and status'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Define thresholds (days)
        thresholds = {
            'CRITICAL': 3,
            'URGENT': 7,
            'NORMAL': 15,
        }
        
        deleted_count = 0
        
        # 1. Delete by Urgency
        for urgency, days in thresholds.items():
            cutoff = now - timedelta(days=days)
            old_requests = BloodRequest.objects.filter(
                urgency=urgency,
                created_at__lt=cutoff
            )
            count = old_requests.count()
            if count > 0:
                old_requests.delete()
                self.stdout.write(self.style.SUCCESS(f'Deleted {count} {urgency} requests older than {days} days.'))
                deleted_count += count

        # 2. Delete non-Active requests older than 7 days
        cutoff_inactive = now - timedelta(days=7)
        inactive_requests = BloodRequest.objects.exclude(status='Active').filter(created_at__lt=cutoff_inactive)
        count_inactive = inactive_requests.count()
        if count_inactive > 0:
            inactive_requests.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count_inactive} non-active requests older than 7 days.'))
            deleted_count += count_inactive

        if deleted_count == 0:
            self.stdout.write(self.style.SUCCESS('No old requests to delete.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Cleanup complete. Total deleted: {deleted_count}'))
