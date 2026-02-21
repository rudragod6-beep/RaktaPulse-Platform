# Standard library imports
import os
import platform
import math
import json

# Django core
from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

# Local apps
from .models import (
    Donor, BloodRequest, BloodBank, VaccineRecord, UserProfile, 
    BLOOD_GROUPS, DonationEvent, Notification, Hospital, 
    Message, Badge, HealthReport
)
from .forms import UserUpdateForm, ProfileUpdateForm, UserRegisterForm

# --- Emergency & Location Helpers ---

@login_required
@csrf_exempt
def emergency_sms(request):
    """
    Demo view for triggering 'SMS' alerts. 
    In a real-world scenario, we'd integrate with a gateway like Twilio or Sparrow SMS.
    """
    if request.method == "POST":
        try:
            # Handle both JSON and Form data because users are unpredictable
            data = json.loads(request.body)
            blood_group = data.get('blood_group')
            lat = data.get('latitude')
            lng = data.get('longitude')
        except (json.JSONDecodeError, AttributeError):
            blood_group = request.POST.get('blood_group')
            lat = request.POST.get('latitude')
            lng = request.POST.get('longitude')
        
        if not (blood_group and lat and lng):
            return JsonResponse({'status': 'error', 'message': 'Blood group and coordinates are required.'}, status=400)
            
        try:
            u_lat = float(lat)
            u_lng = float(lng)
            
            # Simple proximity search: 10km radius
            all_donors = Donor.objects.filter(blood_group=blood_group, is_available=True)
            nearby_donors = []
            
            for d in all_donors:
                if d.latitude and d.longitude:
                    dist = haversine(u_lat, u_lng, float(d.latitude), float(d.longitude))
                    if dist <= 10.0:
                        nearby_donors.append(d)
            
            # Send simulated notifications
            count = len(nearby_donors)
            for d in nearby_donors:
                # Simulated SMS/Push notification logic
                pass
                
            return JsonResponse({
                'status': 'success', 
                'message': f'Success! Pinged {count} donors in the area.',
                'count': count
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Something went sideways: {str(e)}'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)

@login_required
@csrf_exempt
@require_POST
def update_location(request):
    try:
        data = json.loads(request.body)
        lat = data.get('latitude')
        lng = data.get('longitude')
        
        if lat and lng:
            profile = request.user.profile
            profile.latitude = lat
            profile.longitude = lng
            profile.last_location_update = timezone.now()
            profile.save()
            return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

def hospital_list(request):
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    hospitals = Hospital.objects.all()
    hospital_list_data = list(hospitals)
    
    if user_lat and user_lng:
        try:
            u_lat = float(user_lat)
            u_lng = float(user_lng)
            for h in hospital_list_data:
                if h.latitude and h.longitude:
                    h.distance = haversine(u_lat, u_lng, float(h.latitude), float(h.longitude))
                else:
                    h.distance = 999999
            hospital_list_data.sort(key=lambda x: x.distance)
        except ValueError:
            hospital_list_data.sort(key=lambda x: x.name)
    else:
        hospital_list_data.sort(key=lambda x: x.name)
        
    return render(request, 'core/hospital_list.html', {'hospitals': hospital_list_data})

@login_required
def profile(request):
    # Ensure user has a profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
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

@login_required
@require_POST
def delete_personal_info(request):
    """View to clear non-essential personal information."""
    user = request.user
    profile = user.profile
    
    # Clear User fields
    user.first_name = ""
    user.last_name = ""
    user.save()
    
    # Clear Profile fields
    profile.bio = ""
    profile.location = ""
    profile.phone = ""
    profile.birth_date = None
    profile.profile_pic = None
    # We keep blood_group as it's often essential for the app's functionality (blood donation)
    # but we can clear it if the user really wants to. 
    # For now, let's just clear the "soft" personal info.
    profile.save()
    
    messages.success(request, "Your non-essential personal information has been cleared.")
    return redirect('profile')

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
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile = user.profile
            profile.blood_group = form.cleaned_data.get('blood_group')
            profile.location = form.cleaned_data.get('location')
            profile.phone = form.cleaned_data.get('phone')
            profile.save()
            
            login(request, user)
            messages.success(request, f"Welcome to RaktaPulse, {user.username}! You are now a registered donor.")
            return redirect("home")
    else:
        form = UserRegisterForm()
    return render(request, "core/register.html", {"form": form})

def welcome(request):
    """Render a beautiful animated welcome page."""
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, "core/welcome.html")

def home(request):
    """Render the RaktaPulse Dashboard."""
    query_blood = request.GET.get('blood_group', '')
    query_location = request.GET.get('location', '')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')

    # Ensure default badges exist
    if Badge.objects.count() == 0:
        Badge.objects.create(name='First-Time Donor', description='Completed your first donation!', icon_class='fas fa-award')
        Badge.objects.create(name='Community Hero', description='Completed 5 donations!', icon_class='fas fa-medal')
        Badge.objects.create(name='Life Saver', description='Completed 10+ donations!', icon_class='fas fa-heart')

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
    demo_donations = 157
    demo_donors = 48
    
    actual_completed = DonationEvent.objects.filter(is_completed=True).count()
    completed_donations = actual_completed + demo_donations

    stats = {
        "total_donors": Donor.objects.count() + demo_donors,
        "active_requests": BloodRequest.objects.filter(status='Active').count(),
        "total_stock": sum([
            bb.stock_a_plus + bb.stock_a_minus + bb.stock_b_plus + bb.stock_b_minus +
            bb.stock_o_plus + bb.stock_o_minus + bb.stock_ab_plus + bb.stock_ab_minus
            for bb in blood_banks
        ]),
        "total_capacity": sum([bb.total_capacity * 8 for bb in blood_banks]), # 8 blood types
        "vaccinated_percentage": 0,
        "completed_donations": completed_donations,
        "lives_saved": completed_donations * 3
    }
    
    total_d = stats["total_donors"]
    if total_d > 0:
        vaccinated_count = Donor.objects.filter(vaccination_status__icontains='Fully').count()
        stats["vaccinated_percentage"] = int((vaccinated_count / total_d) * 100)

    myths_vs_facts = [
        {"myth": "Donating blood is painful.", "fact": "You only feel a quick pinch, like a mosquito bite."},
        {"myth": "I'm too old to donate.", "fact": "There is no upper age limit as long as you're healthy."},
        {"myth": "It takes all day to donate.", "fact": "The actual donation takes about 10 minutes, the whole process is under an hour."},
        {"myth": "Giving blood makes you weak.", "fact": "Your body replaces fluids within 24 hours and cells within weeks."},
        {"myth": "I can't donate because I have high BP.", "fact": "As long as it's within 180/100 at the time of donation, you're fine."},
    ]

    context = {
        "donors": donor_list_data[:8],
        "blood_requests": blood_requests[:6],
        "blood_banks": blood_banks,
        "blood_groups": [g[0] for g in BLOOD_GROUPS],
        "stats": stats,
        "project_name": "RaktaPulse",
        "current_time": timezone.now(),
        "myths_vs_facts": myths_vs_facts,
    }
    
    if request.user.is_authenticated:
        # Get active involvements
        involved_events = DonationEvent.objects.filter(
            (Q(donor_user=request.user) | Q(request__user=request.user)),
            is_completed=False
        )
        context["involved_events"] = involved_events
        context["user_badges"] = request.user.profile.badges.all()

    return render(request, "core/index.html", context)

def donor_list(request):
    query = request.GET.get('q', '')
    blood_group = request.GET.get('blood_group', '')
    district = request.GET.get('district', '')
    user_lat = request.GET.get('lat')
    user_lng = request.GET.get('lng')
    
    donors = Donor.objects.all()
    if query:
        donors = donors.filter(Q(name__icontains=query) | Q(location__icontains=query))
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
        image = request.FILES.get('image')
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
                image=image,
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
        'selected_hospital': request.GET.get('hospital', ''),
    }
    return render(request, 'core/request_blood.html', context)

@login_required
@login_required
def vaccination_dashboard(request):
    records = VaccineRecord.objects.filter(user=request.user).order_by('-date_taken')
    reports = HealthReport.objects.filter(user=request.user).order_by('-report_date')
    context = {
        'records': records,
        'reports': reports,
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
        photo = request.FILES.get('photo')
        
        if vaccine_name and dose_number and date_taken:
            VaccineRecord.objects.create(
                user=request.user,
                vaccine_name=vaccine_name,
                dose_number=dose_number,
                date_taken=date_taken,
                location=location,
                center_name=center_name,
                notes=notes,
                photo=photo
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
    
    # Prevent requester from volunteering for their own request
    if blood_request.user == request.user:
        messages.error(request, "You cannot volunteer for your own blood request.")
        return redirect('blood_request_list')
    
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
    # Only the requester or the donor can mark as complete
    if request.user == event.donor_user or (event.request.user and request.user == event.request.user):
        event.is_completed = True
        event.save()
        
        # Award Badges Logic
        donor_profile = event.donor_user.profile
        completed_count = DonationEvent.objects.filter(donor_user=event.donor_user, is_completed=True).count()
        
        if completed_count >= 1:
            badge = Badge.objects.filter(name='First-Time Donor').first()
            if badge:
                donor_profile.badges.add(badge)
        
        if completed_count >= 5:
            badge = Badge.objects.filter(name='Community Hero').first()
            if badge:
                donor_profile.badges.add(badge)

        if completed_count >= 10:
            badge = Badge.objects.filter(name='Life Saver').first()
            if badge:
                donor_profile.badges.add(badge)

        # Notify both
        Notification.objects.create(
            user=event.donor_user,
            message=f"Thank you for your donation to {event.request.patient_name}! You've earned recognition for your impact."
        )
        if event.request.user:
            Notification.objects.create(
                user=event.request.user,
                message=f"We hope the donation for {event.request.patient_name} went well."
            )
        
        messages.success(request, "Donation marked as completed. Thank you!")
    else:
        messages.error(request, "You are not authorized to complete this event.")
        
    return redirect('home')

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

def public_profile(request, username):
    user = User.objects.get(username=username)
    profile = user.profile
    donor_profile = getattr(user, 'donor_profile', None)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'donor': donor_profile,
    }
    return render(request, 'core/public_profile.html', context)

@login_required
def inbox(request):
    # Get all users the current user has messaged or received messages from
    sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    user_ids = set(list(sent_to) + list(received_from))
    
    users = User.objects.filter(id__in=user_ids)
    
    # Get last message for each conversation
    conversations = []
    for user in users:
        last_message = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=user)) |
            (Q(sender=user) & Q(receiver=request.user))
        ).order_by('-timestamp').first()
        conversations.append({
            'user': user,
            'last_message': last_message
        })
    
    conversations.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    
    return render(request, 'core/inbox.html', {'conversations': conversations})

@login_required
def chat(request, username):
    other_user = User.objects.get(username=username)
    if request.method == "POST":
        content = request.POST.get('content')
        attachment = request.FILES.get('attachment')
        sticker_id = request.POST.get('sticker_id')
        
        msg_type = 'text'
        if sticker_id:
            msg_type = 'sticker'
        elif attachment:
            content_type = attachment.content_type
            if content_type.startswith('image/'):
                msg_type = 'image'
            elif content_type.startswith('video/'):
                msg_type = 'video'
            else:
                msg_type = 'file'
        
        if content or attachment or sticker_id:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=content,
                attachment=attachment,
                message_type=msg_type,
                sticker_id=sticker_id
            )
            return redirect('chat', username=username)
            
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    # Mark as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'core/chat.html', {'other_user': other_user, 'chat_messages': messages})

@login_required
def upload_health_report(request):
    if request.method == "POST":
        title = request.POST.get('title')
        hospital_name = request.POST.get('hospital_name')
        report_file = request.FILES.get('report_file')
        description = request.POST.get('description')
        report_date = request.POST.get('report_date')
        next_test_date = request.POST.get('next_test_date')
        allow_notifications = request.POST.get('allow_notifications') == 'on'
        
        if title and report_file and report_date:
            HealthReport.objects.create(
                user=request.user,
                title=title,
                hospital_name=hospital_name,
                report_file=report_file,
                description=description,
                report_date=report_date,
                next_test_date=next_test_date if next_test_date else None,
                allow_notifications=allow_notifications
            )
            messages.success(request, "Health report uploaded successfully!")
            return redirect('vaccination_dashboard')
        else:
            messages.error(request, "Please fill in all required fields.")
            
    return render(request, 'core/upload_health_report.html')
