from django.urls import path
from . import views

urlpatterns = [
    # Landing & Dashboard
    path("", views.welcome, name="welcome"),
    path("dashboard/", views.home, name="home"),
    
    # Authentication
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    
    # User Profile & Social
    path("profile/", views.profile, name="profile"),
    path("profile/<str:username>/", views.public_profile, name="public_profile"),
    path("inbox/", views.inbox, name="inbox"),
    path("chat/<str:username>/", views.chat, name="chat"),
    path("notifications/", views.notifications_view, name="notifications"),
    path("delete-personal-info/", views.delete_personal_info, name="delete_personal_info"),
    
    # Donor & Blood Management
    path("donors/", views.donor_list, name="donor_list"),
    path("register-donor/", views.register_donor, name="register_donor"),
    path("requests/", views.blood_request_list, name="blood_request_list"),
    path("request-blood/", views.request_blood, name="request_blood"),
    path("volunteer/<int:request_id>/", views.volunteer_for_request, name="volunteer_for_request"),
    path("complete-donation/<int:event_id>/", views.complete_donation, name="complete_donation"),
    
    # Health & Medical
    path("vaccination/", views.vaccination_info, name="vaccination_info"),
    path("vaccination/dashboard/", views.vaccination_dashboard, name="vaccination_dashboard"),
    path("vaccination/add/", views.add_vaccination, name="add_vaccination"),
    path("reports/upload/", views.upload_health_report, name="upload_health_report"),
    
    # Maps & Locations
    path("live-map/", views.live_map, name="live_map"),
    path("banks/", views.blood_bank_list, name="blood_bank_list"),
    path("hospitals/", views.hospital_list, name="hospital_list"),
    path("update-location/", views.update_location, name="update_location"),
    path("emergency-sms/", views.emergency_sms, name="emergency_sms"),
]
