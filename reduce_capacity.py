import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import BloodBank

def run():
    banks = BloodBank.objects.all()
    for bank in banks:
        bank.total_capacity = 200 # Reduced from 1000
        bank.save()
    print("Capacity reduced for all blood banks.")

if __name__ == "__main__":
    run()
