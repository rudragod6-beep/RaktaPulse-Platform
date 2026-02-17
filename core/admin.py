from django.contrib import admin
from .models import Donor, BloodRequest, BloodBank, VaccineRecord

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    list_display = ('vaccine_name', 'user', 'dose_number', 'date_taken', 'location')
    list_filter = ('vaccine_name', 'date_taken')
    search_fields = ('vaccine_name', 'user__username', 'location')

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
