from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        # For existing users, ensure profile exists
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
        instance.profile.save()

@receiver(post_save, sender=UserProfile)
def sync_donor_profile(sender, instance, **kwargs):
    if instance.blood_group:
        donor, created = Donor.objects.get_or_create(user=instance.user)
        donor.name = f"{instance.user.first_name} {instance.user.last_name}".strip() or instance.user.username
        donor.blood_group = instance.blood_group
        donor.location = instance.location
        donor.phone = instance.phone
        donor.save()

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
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donor_profile')
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

class Hospital(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name

class BloodRequest(models.Model):
    URGENCY_LEVELS = [
        ('CRITICAL', 'Critical'),
        ('URGENT', 'Urgent'),
        ('NORMAL', 'Normal'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_requests', null=True, blank=True)
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
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
    total_capacity = models.IntegerField(default=1000)

    def __str__(self):
        return self.name

class DonationEvent(models.Model):
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    request = models.ForeignKey(BloodRequest, on_delete=models.CASCADE, related_name='donations')
    donor_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='my_donations')
    date = models.DateTimeField(default=timezone.now)
    is_completed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Donation by {self.donor.name} for {self.request.patient_name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:20]}..."

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"
