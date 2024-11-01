from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from Restaurant_handling.models import DieteryPreference
from .models import Business, CustomUser
from django.apps import apps
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
    contact_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter contact number'
        })
    )
    opening_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'  # HTML5 time input
        })
    )
    closing_time = forms.TimeField(
        widget=forms.TimeInput(attrs={
            'class': 'form-control',
            'type': 'time'  # HTML5 time input
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        opening_time = cleaned_data.get('opening_time')
        closing_time = cleaned_data.get('closing_time')
        
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
    class Meta:
        model = Business
        fields = [
            'business_name', 'business_address', 'business_description', 
            'business_tax_code', 'contact_number', 'opening_time', 
            'closing_time', 'business_image', 'cuisine'
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
            'opening_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'closing_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'business_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }