import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Donor, BloodBank

# Kathmandu center approx: 27.7172, 85.3240
def update_coords():
    for donor in Donor.objects.all():
        donor.latitude = 27.7172 + (random.random() - 0.5) * 0.1
        donor.longitude = 85.3240 + (random.random() - 0.5) * 0.1
        donor.save()
    
    for bank in BloodBank.objects.all():
        bank.latitude = 27.7172 + (random.random() - 0.5) * 0.1
        bank.longitude = 85.3240 + (random.random() - 0.5) * 0.1
        bank.save()
    
    print("Updated coordinates for donors and banks.")

if __name__ == "__main__":
    update_coords()
