from django.urls import path

from .views import (
    home, login_view, logout_view, register_view, donor_list, 
    blood_request_list, blood_bank_list, vaccination_info, 
    vaccination_dashboard, add_vaccination, live_map, 
    request_blood, profile, volunteer_for_request, 
    complete_donation, submit_feedback, notifications_view,
    register_donor
)

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("profile/", profile, name="profile"),
    path("donors/", donor_list, name="donor_list"),
    path("requests/", blood_request_list, name="blood_request_list"),
    path("banks/", blood_bank_list, name="blood_bank_list"),
    path("vaccination/", vaccination_info, name="vaccination_info"),
    path("vaccination/dashboard/", vaccination_dashboard, name="vaccination_dashboard"),
    path("vaccination/add/", add_vaccination, name="add_vaccination"),
    path("live-map/", live_map, name="live_map"),
    path("request-blood/", request_blood, name="request_blood"),
    path("volunteer/<int:request_id>/", volunteer_for_request, name="volunteer_for_request"),
    path("complete-donation/<int:event_id>/", complete_donation, name="complete_donation"),
    path("feedback/", submit_feedback, name="submit_feedback"),
    path("notifications/", notifications_view, name="notifications"),
    path("register-donor/", register_donor, name="register_donor"),
]
