import os
import platform
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from .models import Donor, BloodRequest, BloodBank
import math

def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in km
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("home")

def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "core/register.html", {"form": form})

def home(request):
    """Render the RaktaPulse Dashboard experience."""
    query_blood = request.GET.get('blood_group', '')
    query_location = request.GET.get('location', '')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    donors = Donor.objects.all()
    if query_blood:
        donors = donors.filter(blood_group=query_blood)
    if query_location:
        donors = donors.filter(location__icontains=query_location)
    
    donor_list_data = list(donors)
    
    if user_lat and user_lng:
        try:
            u_lat = float(user_lat)
            u_lng = float(user_lng)
            for d in donor_list_data:
                if d.latitude and d.longitude:
                    d.distance = haversine(u_lat, u_lng, float(d.latitude), float(d.longitude))
                else:
                    d.distance = 999999 # Very far
            donor_list_data.sort(key=lambda x: x.distance)
        except ValueError:
            donor_list_data.sort(key=lambda x: (-x.is_available, x.name))
    else:
        donor_list_data.sort(key=lambda x: (-x.is_available, x.name))

    blood_requests = BloodRequest.objects.filter(status='Active').order_by('-urgency', '-created_at')
    blood_banks = BloodBank.objects.all()

    # Stats for Dashboard
    stats = {
        "total_donors": Donor.objects.count(),
        "active_requests": BloodRequest.objects.filter(status='Active').count(),
        "total_stock": sum([
            bb.stock_a_plus + bb.stock_a_minus + bb.stock_b_plus + bb.stock_b_minus +
            bb.stock_o_plus + bb.stock_o_minus + bb.stock_ab_plus + bb.stock_ab_minus
            for bb in blood_banks
        ]),
        "vaccinated_percentage": 0
    }
    
    total_d = stats["total_donors"]
    if total_d > 0:
        vaccinated_count = Donor.objects.filter(vaccination_status__icontains='Fully').count()
        stats["vaccinated_percentage"] = int((vaccinated_count / total_d) * 100)

    context = {
        "donors": donor_list_data[:8],
        "blood_requests": blood_requests[:6],
        "blood_banks": blood_banks,
        "blood_groups": [g[0] for g in Donor.BLOOD_GROUPS],
        "stats": stats,
        "project_name": "RaktaPulse",
        "current_time": timezone.now(),
    }
    return render(request, "core/index.html", context)

def donor_list(request):
    blood_group = request.GET.get('blood_group', '')
    district = request.GET.get('district', '')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    donors = Donor.objects.all()
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if district:
        donors = donors.filter(district__icontains=district)
    
    donor_list_data = list(donors)
    
    if user_lat and user_lng:
        try:
            u_lat = float(user_lat)
            u_lng = float(user_lng)
            for d in donor_list_data:
                if d.latitude and d.longitude:
                    d.distance = haversine(u_lat, u_lng, float(d.latitude), float(d.longitude))
                else:
                    d.distance = 999999
            donor_list_data.sort(key=lambda x: x.distance)
        except ValueError:
            donor_list_data.sort(key=lambda x: (-x.is_verified, x.name))
    else:
        donor_list_data.sort(key=lambda x: (-x.is_verified, x.name))
    
    context = {
        'donors': donor_list_data,
        'blood_groups': [g[0] for g in Donor.BLOOD_GROUPS],
    }
    return render(request, 'core/donor_list.html', context)

def blood_request_list(request):
    requests = BloodRequest.objects.all().order_by('-created_at')
    context = {
        'requests': requests,
    }
    return render(request, 'core/blood_request_list.html', context)

def blood_bank_list(request):
    banks = BloodBank.objects.all()
    context = {
        'banks': banks,
    }
    return render(request, 'core/blood_bank_list.html', context)

def vaccination_info(request):
    stats = {
        "total_donors": Donor.objects.count(),
        "vaccinated_count": Donor.objects.filter(vaccination_status__icontains='Fully').count(),
    }
    if stats["total_donors"] > 0:
        stats["percentage"] = int((stats["vaccinated_count"] / stats["total_donors"]) * 100)
    else:
        stats["percentage"] = 0
    
    return render(request, 'core/vaccination_info.html', {'stats': stats})
