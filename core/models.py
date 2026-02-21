from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# --- Constants & Choices ---

BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('O+', 'O+'), ('O-', 'O-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
]

# --- Models ---

class Badge(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    icon_class = models.CharField(max_length=50, default='fas fa-medal') # FontAwesome

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    last_location_update = models.DateTimeField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics', blank=True, null=True)
    badges = models.ManyToManyField(Badge, blank=True, related_name='users')

    def __str__(self):
        return f"{self.user.username}'s Profile"

# --- Signals for Data Consistency ---

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Auto-creates a profile when a new User is registered."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        # Fallback for users created without signals (e.g. management commands)
        if not hasattr(instance, 'profile'):
            UserProfile.objects.create(user=instance)
        instance.profile.save()

@receiver(post_save, sender=UserProfile)
def sync_donor_profile(sender, instance, **kwargs):
    """Keeps the Donor record in sync with the UserProfile."""
    if instance.blood_group:
        donor, _ = Donor.objects.get_or_create(user=instance.user)
        # Use first/last name if available, otherwise fallback to username
        full_name = f"{instance.user.first_name} {instance.user.last_name}".strip()
        donor.name = full_name or instance.user.username
        
        donor.blood_group = instance.blood_group
        donor.location = instance.location
        donor.latitude = instance.latitude
        donor.longitude = instance.longitude
        donor.phone = instance.phone
        donor.save()

# --- Health & Medical Records ---

class VaccineRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vaccine_records')
    vaccine_name = models.CharField(max_length=100)
    dose_number = models.PositiveIntegerField(default=1)
    date_taken = models.DateField()
    location = models.CharField(max_length=255)
    center_name = models.CharField(max_length=255, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='vaccine_photos/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vaccine_name} (Dose {self.dose_number}) - {self.user.username}"

# --- Core Blood Donation Models ---

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
        status = "Verified" if self.is_verified else "Pending"
        return f"{self.name} [{self.blood_group}] - {status}"

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
    image = models.ImageField(upload_to='blood_requests/', null=True, blank=True)
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
    MESSAGE_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('file', 'File'),
        ('sticker', 'Sticker'),
    ]
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    message_type = models.CharField(max_length=10, choices=MESSAGE_TYPES, default='text')
    sticker_id = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} at {self.timestamp}"

class HealthReport(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_reports')
    title = models.CharField(max_length=200)
    hospital_name = models.CharField(max_length=255, blank=True, null=True)
    report_file = models.FileField(upload_to='health_reports/')
    description = models.TextField(blank=True, null=True)
    report_date = models.DateField(default=timezone.now)
    next_test_date = models.DateField(blank=True, null=True)
    allow_notifications = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report: {self.title} for {self.user.username}"
