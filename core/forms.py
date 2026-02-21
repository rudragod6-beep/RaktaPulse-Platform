from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile, BLOOD_GROUPS

# Registration

class UserRegisterForm(UserCreationForm):
    """Custom registration form to capture blood group and location."""
    email = forms.EmailField(required=True)
    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS, required=True)
    location = forms.CharField(max_length=255, required=True)
    phone = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ['username', 'email']

# Profile Management

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'location', 'phone', 'birth_date', 'blood_group', 'profile_pic']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Tell us a bit about yourself...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Current City/Area'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+977...'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'blood_group': forms.Select(attrs={'class': 'form-control'}, choices=BLOOD_GROUPS),
            'profile_pic': forms.FileInput(attrs={'class': 'form-control'}),
        }
