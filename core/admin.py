from django.contrib import admin
from .models import Donor, BloodRequest, BloodBank

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'location', 'is_available')
    list_filter = ('blood_group', 'is_available')
    search_fields = ('name', 'location')

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'blood_group', 'urgency', 'status', 'created_at')
    list_filter = ('blood_group', 'urgency', 'status')
    search_fields = ('patient_name', 'hospital')

@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
