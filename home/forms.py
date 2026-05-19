# forms.py

from django import forms
from django.contrib.auth.models import User
from .models import Complaint, Officer

# Pre-shared codes for officer registration
VALID_OFFICER_CODES = [
    'PWD2025',  # Example: PWD department code
    'KWA2025',  # KWA department code
    'MUN2025',  # Municipality department code
    'PAN2025',  # Panchayat department code
]

# ================= Complaint Form =================
class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['subject', 'description', 'issue_type', 'location', 'image', 'email', 'google_maps_location']

# ================= User Registration Form =================
class UserRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter a username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a password'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}),
        required=True
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

# ================= Officer Registration Form =================
class OfficerRegistrationForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter a username', 'id': 'id_username', 'class': 'input'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Enter a password', 'id': 'id_password', 'class': 'input'}),
        required=True
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'id': 'id_confirm_password', 'class': 'input'}),
        required=True
    )
    registration_code = forms.CharField(
        max_length=50,
        required=True,
        help_text="Enter your pre-shared officer code",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your officer code', 'class': 'input'})
    )
    department = forms.ChoiceField(
        choices=Officer.DEPARTMENTS,
        required=True,
        widget=forms.Select(attrs={'class': 'input'})
    )

    class Meta:
        model = Officer
        fields = ['officer_id', 'email']
        widgets = {
            'officer_id': forms.TextInput(attrs={'placeholder': 'Officer ID', 'class': 'input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address', 'class': 'input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_officer_id(self):
        officer_id = self.cleaned_data.get('officer_id')
        if Officer.objects.filter(officer_id=officer_id).exists():
            raise forms.ValidationError("Officer ID already exists")
        return officer_id

    def clean_registration_code(self):
        code = self.cleaned_data.get('registration_code')
        if code not in VALID_OFFICER_CODES:
            raise forms.ValidationError("Invalid registration code")
        return code

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data

# ================= Complaint Status Form =================
class ComplaintStatusForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status']
