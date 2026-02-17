from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class VaccineRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vaccine_records')
    vaccine_name = models.CharField(max_length=100)
    dose_number = models.PositiveIntegerField(default=1)
    date_taken = models.DateField()
    location = models.CharField(max_length=255)
    center_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vaccine_name} - Dose {self.dose_number} for {self.user.username}"

class Donor(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]
    name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    district = models.CharField(max_length=100, default='Kathmandu')
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    citizenship_no = models.CharField(max_length=50, null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    vaccination_status = models.CharField(max_length=100, default='Unknown')
    last_vaccination_date = models.DateField(null=True, blank=True)
    avatar_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.blood_group}) - {'Verified' if self.is_verified else 'Unverified'}"

class BloodRequest(models.Model):
    URGENCY_LEVELS = [
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent'),
        ('NORMAL', 'Normal'),
    ]
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=Donor.BLOOD_GROUPS)
    location = models.CharField(max_length=255)
    urgency = models.CharField(max_length=10, choices=URGENCY_LEVELS, default='NORMAL')
    hospital = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_number = models.CharField(max_length=20)
    required_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, default='Active')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.blood_group} for {self.patient_name}"

class BloodBank(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    is_24_7 = models.BooleanField(default=True)
    stock_a_plus = models.IntegerField(default=0)
    stock_a_minus = models.IntegerField(default=0)
    stock_b_plus = models.IntegerField(default=0)
    stock_b_minus = models.IntegerField(default=0)
    stock_o_plus = models.IntegerField(default=0)
    stock_o_minus = models.IntegerField(default=0)
    stock_ab_plus = models.IntegerField(default=0)
    stock_ab_minus = models.IntegerField(default=0)

    def __str__(self):
        return self.name
