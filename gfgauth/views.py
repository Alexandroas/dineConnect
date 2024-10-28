from django.shortcuts import render, redirect
from allauth.account.forms import SignupForm
from django.views import View
from django.contrib.auth import authenticate, login as auth_login, logout
from django.apps import apps
from django.utils import timezone
from django.db import models
from .models import Business
from django.contrib.auth.models import Group
from .forms import UserLoginForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from .forms import UserUpdateForm, BusinessUserRegistrationForm

from django.apps import apps

def home(request):
    Business = apps.get_model('gfgauth', 'Business')
    Cuisine = apps.get_model('Restaurant_handling', 'Cuisine')
    
    businesses = Business.objects.prefetch_related('cuisine').all()
    cuisines = Cuisine.objects.all()
    
    context = {
        'businesses': businesses,
        'cuisines': cuisines
    }
    
    return render(request, 'gfgauth/home.html', context)

def logout_view(request):
    logout(request)
    return redirect('/')

def register_business(request):
    if request.method == 'POST':
        form = BusinessUserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Create the custom user first
                business_user = form.save(commit=False)
                # Make sure required fields are set
                business_user.email = form.cleaned_data['email']
                business_user.username = form.cleaned_data['username']
                business_user.first_name = form.cleaned_data['first_name']
                business_user.last_name = form.cleaned_data['last_name']
                business_user.set_password(form.cleaned_data['password1'])
                business_user.save()
                print("Business user created:", business_user)
                print("Business user ID:", business_user.id)

                # Handle business group
                try:
                    business_group = Group.objects.get(name='Business')
                except Group.DoesNotExist:
                    business_group = Group.objects.create(name='Business')
                
                # Add user to business group
                business_user.groups.add(business_group)
                print(f"Added user to Business group successfully")

                # Create business record - moved outside the except block
                business = Business.objects.create(
                    business_name=form.cleaned_data['business_name'],
                    business_owner=business_user,
                    business_address=form.cleaned_data['business_address'],
                    business_description=form.cleaned_data['business_description'],
                    business_tax_code=form.cleaned_data['business_tax_code'],
                    contact_number=form.cleaned_data['contact_number'],
                    opening_time=form.cleaned_data['opening_time'],
                    closing_time=form.cleaned_data['closing_time']
                )

                # Handle business image
                if 'business_image' in request.FILES:
                    business.business_image = request.FILES['business_image']
                    business.save()

                # Handle cuisine
                if 'cuisine' in form.cleaned_data:
                    business.cuisine.set(form.cleaned_data['cuisine'])

                print("Business created successfully:", business)

                # Log the user in
                auth_login(request, business_user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('restaurant_home')

            except Exception as e:
                print("Error during registration:", str(e))
                # If something goes wrong, delete the user if it was created
                if 'business_user' in locals():
                    business_user.delete()
                raise

    else:
        form = BusinessUserRegistrationForm()
   
    return render(request, 'gfgauth/register_business.html', {'form': form})
def login(request):
    return render(request, 'gfgauth/login.html')

class SignupView(View):
    def get(self, request):
        return render(request, 'gfgauth/signup.html', {'form': SignupForm()})
    def post(self, request):
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save(request)
            return redirect('home')
        else:
            print(form.errors)
        return render(request, 'gfgauth/signup.html', {'form': form})

def custom_login(request):
    if request.method == "POST":
        form = UserLoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                auth_login(request, user)  # Use the renamed function to avoid conflict
                messages.success(request, f"Hello <b>{user.username}</b>! Successful login!")
                return redirect("home")
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
            
    form = UserLoginForm()
    return render(
        request=request,
        template_name="gfgauth/login.html",
        context={"form": form}
    )
    
@login_required
def password_change(request):
    user = request.user
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been changed!")
            return redirect('login')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
    else:
        form = SetPasswordForm(user)
    return render(request, 'gfgauth/password_change.html', {'form': form})  # Specify a template here

@login_required
def profile(request, username):
    # Get current datetime for comparison
    current_datetime = timezone.now()
    
    # Get all user reservations
    reservations = request.user.reservation_set.all()
    
    # Split into upcoming and past
    upcoming_reservations = reservations.filter(
        models.Q(reservation_date__gt=current_datetime.date()) |
        models.Q(
            reservation_date=current_datetime.date(),
            reservation_time__gt=current_datetime.time()
        )
    ).order_by('reservation_date', 'reservation_time')
    
    past_reservations = reservations.filter(
        models.Q(reservation_date__lt=current_datetime.date()) |
        models.Q(
            reservation_date=current_datetime.date(),
            reservation_time__lte=current_datetime.time()
        )
    ).order_by('-reservation_date', '-reservation_time')

    if request.method == 'POST':
        user = request.user
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save()
            messages.success(request, f'{user_form.username}, Your profile has been changed!')
            return redirect("profile", user_form.username)
        
        for error in list(form.errors.values()):
            messages.error(request, error)
    
    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        return render(
            request=request,
            template_name="gfgauth/profile.html",
            context={
                "form": form,
                "upcoming_reservations": upcoming_reservations,
                "past_reservations": past_reservations
            }
        )
    return redirect("homepage")

