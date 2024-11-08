from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from Restaurant_handling.models import DieteryPreference
from .models import Business, CustomUser, businessHours
from django.apps import apps
from django.db import models
from django.core.exceptions import ValidationError

# forms.py
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=24, required=True)
    last_name = forms.CharField(max_length=24, required=True)
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        label="Profile Picture"
    )
    dietery_preference = forms.ModelMultipleChoiceField(  # Match the model field name
        queryset=DieteryPreference.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dietary Preferences"
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'dietery_preference', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            # Set initial values for dietary preferences
            self.initial['dietery_preference'] = self.instance.dietery_preference.all()
class CustomUserCreationForm(UserCreationForm):
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label="Profile Picture"
    )
    
    dietery_preference = forms.ModelMultipleChoiceField(
        queryset=DieteryPreference.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        label="Dietary Preferences"
    )

    class Meta:
        model = get_user_model()
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'password1', 
            'password2', 
            'profile_image', 
            'dietery_preference'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name != 'dietery_preference':  # Skip dietary preference as it uses checkboxes
                field.widget.attrs['class'] = 'form-control'

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email.'}),
        label="Username or Email*")
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))



class BusinessBasicInfoForm(forms.Form):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'})
    )
    last_name = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'})
    )
    username = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

class BusinessDetailsForm(forms.Form):
    business_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter business name'
        })
    )
    business_address = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'maxlength': '255',
            'rows': 3,
            'placeholder': 'Enter business address'
        })
    )
    business_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'maxlength': '255',
            'rows': 3,
            'placeholder': 'Describe your business'
        })
    )
    business_tax_code = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter tax code'
        })
    )

class BusinessHoursForm(forms.Form):
    # Checkboxes for each day of the week
    monday = forms.BooleanField(required=False, initial=False)
    tuesday = forms.BooleanField(required=False, initial=False)
    wednesday = forms.BooleanField(required=False, initial=False)
    thursday = forms.BooleanField(required=False, initial=False)
    friday = forms.BooleanField(required=False, initial=False)
    saturday = forms.BooleanField(required=False, initial=False)
    sunday = forms.BooleanField(required=False, initial=False)

    opening_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    closing_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    is_closed = forms.BooleanField(
        required=False,
        initial=False,
        label='Closed on selected days'
    )
    shift_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Lunch, Dinner'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        is_closed = cleaned_data.get('is_closed')
        
        # Check if at least one day is selected
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        selected_days = any(cleaned_data.get(day) for day in days)
        
        if not selected_days:
            raise ValidationError("Please select at least one day of the week.")

        if not is_closed:
            if not opening_time or not closing_time:
                raise ValidationError("Opening and closing times are required when the business is open.")
            
            if opening_time and closing_time and opening_time >= closing_time:
                raise ValidationError("Closing time must be later than opening time.")

        return cleaned_data

class BusinessImageForm(forms.Form):
    business_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'  # Accept only image files
        })
    )
    cuisine = forms.ModelMultipleChoiceField(
        queryset=apps.get_model('Restaurant_handling', 'Cuisine').objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )

class BusinessUpdateForm(forms.ModelForm):
    # Add fields for business hours
    monday = forms.BooleanField(required=False, initial=False)
    tuesday = forms.BooleanField(required=False, initial=False)
    wednesday = forms.BooleanField(required=False, initial=False)
    thursday = forms.BooleanField(required=False, initial=False)
    friday = forms.BooleanField(required=False, initial=False)
    saturday = forms.BooleanField(required=False, initial=False)
    sunday = forms.BooleanField(required=False, initial=False)
    
    hours_opening_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    hours_closing_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'
        })
    )
    hours_is_closed = forms.BooleanField(
        required=False,
        initial=False,
        label='Closed on selected days'
    )
    hours_shift_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., Regular Hours'
        })
    )

    class Meta:
        model = Business
        fields = [
            'business_name', 'business_address', 'business_description',
            'business_tax_code', 'contact_number', 'business_image', 'cuisine'
        ]
        widgets = {
            'business_address': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'rows': 3
            }),
            'business_description': forms.Textarea(attrs={
                'class': 'form-control',
                'maxlength': '255',
                'rows': 3
            }),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'business_tax_code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            # Pre-populate business hours if they exist
            for day_number, day_name in businessHours.DAYS_OF_WEEK:
                day_field = day_name.lower()
                hours = instance.business_hours.filter(day_of_week=day_number).first()
                
                if hours:
                    setattr(self.fields[day_field], 'initial', True)
                    if not hours.is_closed:
                        self.fields['hours_opening_time'].initial = hours.opening_time
                        self.fields['hours_closing_time'].initial = hours.closing_time
                    self.fields['hours_is_closed'].initial = hours.is_closed
                    self.fields['hours_shift_name'].initial = hours.shift_name

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            
            # Handle business hours
            days_mapping = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }

            # Delete existing hours
            instance.business_hours.all().delete()

            # Create new hours for selected days
            for day_name, day_number in days_mapping.items():
                if self.cleaned_data.get(day_name):
                    businessHours.objects.create(
                        business=instance,
                        day_of_week=day_number,
                        opening_time=self.cleaned_data['hours_opening_time'] if not self.cleaned_data['hours_is_closed'] else None,
                        closing_time=self.cleaned_data['hours_closing_time'] if not self.cleaned_data['hours_is_closed'] else None,
                        is_closed=self.cleaned_data['hours_is_closed'],
                        shift_name=self.cleaned_data['hours_shift_name']
                    )

        return instance

    def clean(self):
        cleaned_data = super().clean()
        is_closed = cleaned_data.get('hours_is_closed')
        opening_time = cleaned_data.get('hours_opening_time')
        closing_time = cleaned_data.get('hours_closing_time')
        
        # Check if at least one day is selected
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        selected_days = any(cleaned_data.get(day) for day in days)
        
        if not selected_days:
            raise ValidationError("Please select at least one day of the week for business hours.")

        if not is_closed and any(cleaned_data.get(day) for day in days):
            if not opening_time or not closing_time:
                raise ValidationError("Opening and closing times are required when the business is open.")
            
            if opening_time and closing_time and opening_time >= closing_time:
                raise ValidationError("Closing time must be later than opening time.")

        return cleaned_data