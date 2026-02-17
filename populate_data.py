import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Donor, BloodRequest, BloodBank
from django.utils import timezone

def run():
    # Clear existing data
    Donor.objects.all().delete()
    BloodRequest.objects.all().delete()
    BloodBank.objects.all().delete()

    # Create Donors (Nepali Context)
    donors_data = [
        ('Arjun Thapa', 'O+', 'Kathmandu', 'New Baneshwor', '9841000000', 'Fully Vaccinated', True),
        ('Sita Shrestha', 'A-', 'Lalitpur', 'Patan Durbar Square', '9841111111', 'Fully Vaccinated', True),
        ('Rajesh Hamal', 'B+', 'Bhaktapur', 'Suryabinayak', '9841222222', 'Partially Vaccinated', True),
        ('Bipana Thapa', 'AB+', 'Kaski', 'Lakeside, Pokhara', '9841333333', 'Fully Vaccinated', False),
        ('Nischal Basnet', 'O-', 'Rupandehi', 'Butwal', '9841444444', 'Not Vaccinated', False),
        ('Swastima Khadka', 'A+', 'Chitwan', 'Bharatpur', '9841555555', 'Fully Vaccinated', True),
    ]
    for name, bg, dist, loc, ph, vac, ver in donors_data:
        Donor.objects.create(
            name=name, 
            blood_group=bg, 
            district=dist,
            location=loc, 
            phone=ph, 
            is_available=True,
            is_verified=ver,
            citizenship_no=f"123-{random.randint(1000, 9999)}" if ver else None,
            vaccination_status=vac,
            last_vaccination_date=timezone.now().date() - datetime.timedelta(days=random.randint(30, 180))
        )

    # Create Blood Requests (Nepali Context)
    BloodRequest.objects.create(
        patient_name='Ram Bahadur', 
        blood_group='O+', 
        location='Teaching Hospital, Maharajgunj', 
        urgency='CRITICAL',
        hospital='Teaching Hospital',
        contact_number='9800000001'
    )
    BloodRequest.objects.create(
        patient_name='Maya Devi', 
        blood_group='B+', 
        location='Bir Hospital, Kathmandu', 
        urgency='URGENT',
        hospital='Bir Hospital',
        contact_number='9800000002'
    )
    BloodRequest.objects.create(
        patient_name='Hari Prasad', 
        blood_group='AB-', 
        location='Patan Hospital', 
        urgency='NORMAL',
        hospital='Patan Hospital',
        contact_number='9800000003'
    )

    # Create Blood Bank (Nepali Context)
    BloodBank.objects.create(
        name='Nepal Red Cross Society', 
        location='Soalteemode, Kathmandu', 
        contact_number='01-4270650',
        is_24_7=True,
        stock_o_plus=150, 
        stock_o_minus=45,
        stock_a_plus=120,
        stock_a_minus=30,
        stock_b_plus=90,
        stock_b_minus=20,
        stock_ab_plus=40,
        stock_ab_minus=15
    )
    
    BloodBank.objects.create(
        name='Bhaktapur Blood Bank', 
        location='Dudhpati, Bhaktapur', 
        contact_number='01-6612266',
        is_24_7=True,
        stock_o_plus=60, 
        stock_a_plus=45,
        stock_b_plus=30
    )

    print("Sample data populated successfully.")

if __name__ == "__main__":
    run()
