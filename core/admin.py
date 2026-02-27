from django.contrib import admin
import csv
from django.http import HttpResponse
from .models import (
    Donor, BloodRequest, BloodBank, VaccineRecord, 
    DonationEvent, Hospital, UserProfile, Badge, 
    Notification, Message, HealthReport
)

def export_as_csv(self, request, queryset):
    meta = self.model._meta
    field_names = [field.name for field in meta.fields]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={meta}.csv'
    writer = csv.writer(response)

    writer.writerow(field_names)
    for obj in queryset:
        writer.writerow([getattr(obj, field) for field in field_names])

    return response

export_as_csv.short_description = "Export Selected to CSV"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'blood_group', 'location', 'phone')
    list_filter = ('blood_group',)
    search_fields = ('user__username', 'phone', 'location')
    actions = [export_as_csv]

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(VaccineRecord)
class VaccineRecordAdmin(admin.ModelAdmin):
    list_display = ('vaccine_name', 'user', 'dose_number', 'date_taken', 'location')
    list_filter = ('vaccine_name', 'date_taken')
    search_fields = ('vaccine_name', 'user__username', 'location')
    actions = [export_as_csv]

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('name', 'blood_group', 'location', 'is_available', 'is_verified')
    list_filter = ('blood_group', 'is_available', 'is_verified')
    search_fields = ('name', 'location', 'phone')
    actions = [export_as_csv]

@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'phone')
    search_fields = ('name', 'location')

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'blood_group', 'urgency', 'status', 'hospital', 'created_at')
    list_filter = ('blood_group', 'urgency', 'status')
    search_fields = ('patient_name', 'hospital')
    actions = [export_as_csv]

@admin.register(BloodBank)
class BloodBankAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'stock_a_plus', 'stock_b_plus', 'stock_o_plus', 'stock_ab_plus')
    search_fields = ('name', 'location')
    actions = [export_as_csv]

@admin.register(DonationEvent)
class DonationEventAdmin(admin.ModelAdmin):
    list_display = ('donor', 'request', 'date', 'is_completed')
    list_filter = ('is_completed', 'date')
    search_fields = ('donor__name', 'request__patient_name')
    actions = [export_as_csv]

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message_type', 'timestamp', 'is_read')
    list_filter = ('message_type', 'is_read', 'timestamp')

@admin.register(HealthReport)
class HealthReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'hospital_name', 'report_date')
    list_filter = ('report_date',)
    search_fields = ('title', 'user__username', 'hospital_name')
