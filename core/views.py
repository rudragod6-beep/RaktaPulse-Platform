import os
import platform
from django.db import models
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Donor, BloodRequest, BloodBank, VaccineRecord, UserProfile, BLOOD_GROUPS, DonationEvent, Notification, Feedback
from .forms import UserUpdateForm, ProfileUpdateForm
import math

@login_required
def profile(request):
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your account has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'core/profile.html', context)

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
        "total_capacity": sum([bb.total_capacity * 8 for bb in blood_banks]), # 8 blood types
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
        "blood_groups": [g[0] for g in BLOOD_GROUPS],
        "stats": stats,
        "project_name": "RaktaPulse",
        "current_time": timezone.now(),
    }
    
    if request.user.is_authenticated:
        # Get active involvements (where user is donor or requester)
        involved_events = DonationEvent.objects.filter(
            (models.Q(donor_user=request.user) | models.Q(request__user=request.user)),
            is_completed=False
        )
        context["involved_events"] = involved_events

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
        'blood_groups': [g[0] for g in BLOOD_GROUPS],
    }
    return render(request, 'core/donor_list.html', context)

def blood_request_list(request):
    status = request.GET.get('status', '')
    requests = BloodRequest.objects.all()
    if status:
        requests = requests.filter(status=status)
    
    requests = requests.order_by('-created_at')
    context = {
        'requests': requests,
        'current_status': status,
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
                user=request.user if request.user.is_authenticated else None,
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
        'blood_groups': [g[0] for g in BLOOD_GROUPS],
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

@login_required
def volunteer_for_request(request, request_id):
    blood_request = BloodRequest.objects.get(id=request_id)
    donor_profile = getattr(request.user, 'donor_profile', None)
    
    if not donor_profile:
        messages.error(request, "You need to be registered as a donor to volunteer.")
        return redirect('donor_list')
    
    # Check if already volunteered
    if DonationEvent.objects.filter(donor=donor_profile, request=blood_request).exists():
        messages.warning(request, "You have already volunteered for this request.")
    else:
        DonationEvent.objects.create(
            donor=donor_profile,
            request=blood_request,
            donor_user=request.user
        )
        messages.success(request, "Thank you for volunteering! The requester has been notified.")
        
        # Notify the requester
        if blood_request.user:
            Notification.objects.create(
                user=blood_request.user,
                message=f"Donor {request.user.username} has volunteered to help {blood_request.patient_name}!"
            )
            
    return redirect('blood_request_list')

@login_required
def complete_donation(request, event_id):
    event = DonationEvent.objects.get(id=event_id)
    # Only the requester or the donor can mark as complete (for simplicity, letting both)
    if request.user == event.donor_user or (event.request.user and request.user == event.request.user):
        event.is_completed = True
        event.save()
        
        # Notify both
        Notification.objects.create(
            user=event.donor_user,
            message=f"Thank you for your donation to {event.request.patient_name}! Your feedback is valuable to us."
        )
        if event.request.user:
            Notification.objects.create(
                user=event.request.user,
                message=f"We hope the donation for {event.request.patient_name} went well. Please share your feedback!"
            )
        
        messages.success(request, "Donation marked as completed. Thank you!")
    else:
        messages.error(request, "You are not authorized to complete this event.")
        
    return redirect('home')

@login_required
def submit_feedback(request):
    if request.method == "POST":
        content = request.POST.get('content')
        rating = request.POST.get('rating')
        if content:
            Feedback.objects.create(
                user=request.user,
                content=content,
                rating=rating if rating else 5
            )
            messages.success(request, "Thank you for your feedback!")
            return redirect('home')
    return render(request, 'core/feedback.html')

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    # Mark as read when viewed
    notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'core/notifications.html', {'notifications': notifications})

@login_required
def register_donor(request):
    if hasattr(request.user, 'donor_profile'):
        messages.info(request, "You are already registered as a donor.")
        return redirect('profile')
        
    if request.method == "POST":
        blood_group = request.POST.get('blood_group')
        location = request.POST.get('location')
        phone = request.POST.get('phone')
        
        if blood_group and phone:
            Donor.objects.create(
                user=request.user,
                name=request.user.username,
                blood_group=blood_group,
                location=location,
                phone=phone,
                is_available=True
            )
            messages.success(request, "Congratulations! You are now a registered donor.")
            return redirect('donor_list')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'core/register_donor.html', {'blood_groups': [g[0] for g in BLOOD_GROUPS]})
