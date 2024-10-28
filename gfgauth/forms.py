from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Business, CustomUser
from django.apps import apps
class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = get_user_model()
        fields = [
            'first_name',
            'last_name',
            'email',
        ]

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name', 'username']

class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(UserLoginForm, self).__init__(*args, **kwargs)

    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username or Email.'}),
        label="Username or Email*")
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password'}))


class BusinessUserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    username = forms.CharField(max_length=100, required=True)
    business_name = forms.CharField(max_length=100)
    business_address = forms.CharField(widget=forms.Textarea(attrs={'maxlength': '255'})) #TODO: Add Google Maps API
    business_description = forms.CharField(widget=forms.Textarea(attrs={'maxlength': '255'}))
    business_tax_code = forms.CharField(max_length=100)
    contact_number = forms.CharField(max_length=20)
    opening_time = forms.TimeField()
    closing_time = forms.TimeField()
    business_image = forms.ImageField(required=False)
    
    Cuisine = apps.get_model('Restaurant_handling', 'Cuisine')
    
    cuisine = forms.ModelMultipleChoiceField(
        queryset= Cuisine.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'first_name', 'last_name', 
                 'password1', 'password2', 'business_name',
                 'business_address','business_description', 'business_tax_code', 
                 'contact_number', 'opening_time', 'closing_time',
                 'business_image', 'cuisine')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
        