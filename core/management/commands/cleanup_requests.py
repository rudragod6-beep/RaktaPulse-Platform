from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
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

        # 2. Delete non-Active and non-Accepted requests older than 7 days
        cutoff_inactive = now - timedelta(days=7)
        inactive_requests = BloodRequest.objects.exclude(
            Q(status='Active') | Q(status='Accepted')
        ).filter(created_at__lt=cutoff_inactive)
        count_inactive = inactive_requests.count()
        if count_inactive > 0:
            inactive_requests.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count_inactive} non-active/non-accepted requests older than 7 days.'))
            deleted_count += count_inactive

        # 3. For Accepted requests, we keep them for 30 days after acceptance for history
        cutoff_accepted = now - timedelta(days=30)
        old_accepted = BloodRequest.objects.filter(
            status='Accepted',
            accepted_at__lt=cutoff_accepted
        )
        count_accepted = old_accepted.count()
        if count_accepted > 0:
            old_accepted.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {count_accepted} accepted requests older than 30 days.'))
            deleted_count += count_accepted

        if deleted_count == 0:
            self.stdout.write(self.style.SUCCESS('No old requests to delete.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Cleanup complete. Total deleted: {deleted_count}'))
