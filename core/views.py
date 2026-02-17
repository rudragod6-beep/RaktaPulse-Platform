import os
import platform
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Donor, BloodRequest, BloodBank, VaccineRecord
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
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
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
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    banks = BloodBank.objects.all()
    bank_list_data = list(banks)
    
    if user_lat and user_lng:
        try:
            u_lat = float(user_lat)
            u_lng = float(user_lng)
            for b in bank_list_data:
                if b.latitude and b.longitude:
                    b.distance = haversine(u_lat, u_lng, float(b.latitude), float(b.longitude))
                else:
                    b.distance = 999999
            bank_list_data.sort(key=lambda x: x.distance)
        except ValueError:
            pass
    
    context = {
        'banks': bank_list_data,
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

def live_map(request):
    """View to display live alerts/requests on a map."""
    active_requests = BloodRequest.objects.filter(status='Active').order_by('-created_at')
    
    # Also include blood banks and donors optionally if we want a full map
    # But focusing on alerts as requested.
    context = {
        'requests': active_requests,
        'title': 'Live Alert Map',
    }
    return render(request, 'core/live_map.html', context)

def request_blood(request):
    """View to create a new blood request with geolocation."""
    if request.method == "POST":
        patient_name = request.POST.get('patient_name')
        blood_group = request.POST.get('blood_group')
        location = request.POST.get('location')
        urgency = request.POST.get('urgency')
        hospital = request.POST.get('hospital')
        contact_number = request.POST.get('contact_number')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        if patient_name and blood_group and hospital and contact_number:
            BloodRequest.objects.create(
                patient_name=patient_name,
                blood_group=blood_group,
                location=location,
                urgency=urgency,
                hospital=hospital,
                contact_number=contact_number,
                latitude=latitude if latitude else None,
                longitude=longitude if longitude else None
            )
            messages.success(request, "Blood request posted successfully! Help is on the way.")
            return redirect('blood_request_list')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    context = {
        'blood_groups': [g[0] for g in Donor.BLOOD_GROUPS],
        'urgency_levels': BloodRequest.URGENCY_LEVELS,
    }
    return render(request, 'core/request_blood.html', context)

@login_required
def vaccination_dashboard(request):
    records = VaccineRecord.objects.filter(user=request.user).order_by('-date_taken')
    context = {
        'records': records,
        'project_name': "RaktaPulse",
    }
    return render(request, 'core/vaccination_dashboard.html', context)

@login_required
def add_vaccination(request):
    if request.method == "POST":
        vaccine_name = request.POST.get('vaccine_name')
        dose_number = request.POST.get('dose_number')
        date_taken = request.POST.get('date_taken')
        location = request.POST.get('location')
        center_name = request.POST.get('center_name')
        notes = request.POST.get('notes')
        
        if vaccine_name and dose_number and date_taken:
            VaccineRecord.objects.create(
                user=request.user,
                vaccine_name=vaccine_name,
                dose_number=dose_number,
                date_taken=date_taken,
                location=location,
                center_name=center_name,
                notes=notes
            )
            messages.success(request, "Vaccination record added successfully!")
            return redirect('vaccination_dashboard')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'core/add_vaccination.html')
