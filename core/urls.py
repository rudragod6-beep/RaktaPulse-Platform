from django.urls import path

from .views import (
    welcome, home, login_view, logout_view, register_view, donor_list, 
    blood_request_list, blood_bank_list, vaccination_info, 
    vaccination_dashboard, add_vaccination, live_map, 
    request_blood, profile, volunteer_for_request, 
    complete_donation, notifications_view,
    register_donor, hospital_list, public_profile, inbox, chat,
    update_location, emergency_sms, delete_personal_info,
    health_report_list, upload_health_report
)

urlpatterns = [
    path("", welcome, name="welcome"),
    path("dashboard/", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("profile/", profile, name="profile"),
    path("profile/<str:username>/", public_profile, name="public_profile"),
    path("inbox/", inbox, name="inbox"),
    path("chat/<str:username>/", chat, name="chat"),
    path("donors/", donor_list, name="donor_list"),
    path("requests/", blood_request_list, name="blood_request_list"),
    path("banks/", blood_bank_list, name="blood_bank_list"),
    path("vaccination/", vaccination_info, name="vaccination_info"),
    path("vaccination/dashboard/", vaccination_dashboard, name="vaccination_dashboard"),
    path("vaccination/add/", add_vaccination, name="add_vaccination"),
    path("reports/", health_report_list, name="health_report_list"),
    path("reports/upload/", upload_health_report, name="upload_health_report"),
    path("live-map/", live_map, name="live_map"),
    path("request-blood/", request_blood, name="request_blood"),
    path("emergency-sms/", emergency_sms, name="emergency_sms"),
    path("volunteer/<int:request_id>/", volunteer_for_request, name="volunteer_for_request"),
    path("complete-donation/<int:event_id>/", complete_donation, name="complete_donation"),
    path("notifications/", notifications_view, name="notifications"),
    path("register-donor/", register_donor, name="register_donor"),
    path("hospitals/", hospital_list, name="hospital_list"),
    path("update-location/", update_location, name="update_location"),
    path("delete-personal-info/", delete_personal_info, name="delete_personal_info"),
]
