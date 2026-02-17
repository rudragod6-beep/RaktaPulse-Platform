from django.urls import path

from .views import home, login_view, logout_view, register_view, donor_list, blood_request_list, blood_bank_list, vaccination_info, vaccination_dashboard, add_vaccination, live_map

urlpatterns = [
    path("", home, name="home"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("register/", register_view, name="register"),
    path("donors/", donor_list, name="donor_list"),
    path("requests/", blood_request_list, name="blood_request_list"),
    path("banks/", blood_bank_list, name="blood_bank_list"),
    path("vaccination/", vaccination_info, name="vaccination_info"),
    path("vaccination/dashboard/", vaccination_dashboard, name="vaccination_dashboard"),
    path("vaccination/add/", add_vaccination, name="add_vaccination"),
    path("live-map/", live_map, name="live_map"),
    path("request-blood/", request_blood, name="request_blood"),
]
