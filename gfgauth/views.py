from django.http import JsonResponse
from django.shortcuts import render, redirect
from allauth.account.forms import SignupForm
from django.views import View
from django.contrib.auth import authenticate, login as auth_login, logout
from django.apps import apps
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import get_user_model
from formtools.wizard.views import SessionWizardView
from django.core.files.storage import FileSystemStorage
from .models import Business, CustomUser
import os
from .forms import CustomUserCreationForm
from main.utils import send_welcome_email
from django.conf import settings
from .forms import (
    BusinessBasicInfoForm,
    BusinessDetailsForm,
    BusinessHoursForm,
    BusinessImageForm,
    UserUpdateForm,
    UserLoginForm)

def home(request):
    Business = apps.get_model('gfgauth', 'Business')
    Cuisine = apps.get_model('Restaurant_handling', 'Cuisine')
    Testimonial = apps.get_model('main', 'Testimonial')  # Add this line
   
    businesses = Business.objects.prefetch_related('cuisine').all()
    is_business = request.user.groups.filter(name='Business').exists()
    cuisines = Cuisine.objects.all()
    testimonials = Testimonial.objects.filter(is_visible=True).select_related('user')  # Add this line
   
    context = {
        'businesses': businesses,
        'cuisines': cuisines,
        'testimonials': testimonials,  # Add this line
        'is_business': is_business
    }
   
    return render(request, 'gfgauth/home.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect('/')

FORMS = [
    ("basic", BusinessBasicInfoForm),
    ("details", BusinessDetailsForm),
    ("hours", BusinessHoursForm),
    ("image", BusinessImageForm),
]

class BusinessRegistrationWizard(SessionWizardView):
    file_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'temp'))
    template_name = "gfgauth/register_business.html"  # Use your existing template

    def get_template_names(self):
        return [self.template_name]

    
    def post(self, *args, **kwargs):
        """Override post to handle the back button without validation"""
        wizard_goto_step = self.request.POST.get('wizard_goto_step', None)
        if wizard_goto_step and wizard_goto_step in self.get_form_list():
            return self.render_goto_step(wizard_goto_step)
        return super().post(*args, **kwargs)

    def render_goto_step(self, goto_step):
        """Helper method to render the form for the goto_step"""
        self.storage.current_step = goto_step
        form = self.get_form(
            step=goto_step,
            data=self.storage.get_step_data(goto_step),
            files=self.storage.get_step_files(goto_step)
        )
        return self.render(form)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        if self.steps.current == self.steps.last:
            context.update({'is_last_step': True})
        return context
    
    def done(self, form_list, **kwargs):
        # Combine all form data
        form_data = {}
        for form in form_list:
            form_data.update(form.cleaned_data)

        try:
            # Create the custom user first
            business_user = CustomUser.objects.create_user(
                username=form_data['username'],
                email=form_data['email'],
                password=form_data['password1'],
                first_name=form_data['first_name'],
                last_name=form_data['last_name']
            )
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

            # Create business record
            business = Business.objects.create(
                business_name=form_data['business_name'],
                business_owner=business_user,
                business_address=form_data['business_address'],
                business_description=form_data['business_description'],
                business_tax_code=form_data['business_tax_code'],
                contact_number=form_data['contact_number'],
                opening_time=form_data['opening_time'],
                closing_time=form_data['closing_time']
            )

            # Handle business image
            if form_data.get('business_image'):
                business.business_image = form_data['business_image']
                business.save()

            # Handle cuisine
            if form_data.get('cuisine'):
                business.cuisine.set(form_data['cuisine'])

            print("Business created successfully:", business)

            # Log the user in
            auth_login(self.request, business_user, 
                      backend='django.contrib.auth.backends.ModelBackend')

            return redirect('restaurant_home')

        except Exception as e:
            print("Error during registration:", str(e))
            # If something goes wrong, delete the user if it was created
            if 'business_user' in locals():
                business_user.delete()
            raise

    def process_step(self, form):
        """Process each step, validating data as needed"""
        cleaned_data = self.get_all_cleaned_data()
        
        # Validate email and username uniqueness in the first step
        if self.steps.current == 'basic':
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            
            if CustomUser.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already in use.')
            
            if CustomUser.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.')

        return super().process_step(form)
def login(request):
    return render(request, 'gfgauth/login.html')

class SignupView(View):
    def get(self, request):
        return render(request, 'gfgauth/signup.html', {'form': CustomUserCreationForm()})
    def post(self, request):
        form = SignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(request)
            send_welcome_email(user)
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
                messages.success(request, f"Hello {user.username}! Successful login!")
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
    # First check if the requested profile matches the logged-in user
    if request.user.username != username:
        messages.error(request, "You can only view and edit your own profile.")
        return redirect("profile", request.user.username)

    # Get user object
    user = get_user_model().objects.filter(username=username).first()
    if not user:
        messages.error(request, "User not found.")
        return redirect("homepage")

    # Get current datetime for comparison
    current_datetime = timezone.now()

    # Get all user reservations
    reservations = user.reservation_set.all()
    # Get user dietery preferences
    dietery_preference = user.dietery_preference.all()
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
        form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user_form = form.save(commit=False)
            user_form.save()
            # Save many-to-many data
            form.save_m2m()
            messages.success(request, f'{user_form.username}, Your profile has been updated!')
            return redirect("profile", user_form.username)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserUpdateForm(instance=user)
    user = get_user_model().objects.filter(username=username).first()
    if user:
        form = UserUpdateForm(instance=user)
        # Get user's favorite restaurants
        favorite_restaurants = user.favourite_restaurants.all()
    context = {
        "form": form,
        "upcoming_reservations": upcoming_reservations,
        "dietery_preference": dietery_preference,
        "past_reservations": past_reservations,
        "user_profile": user,  # Add this to distinguish between logged-in user and profile user
        "favorite_restaurants": favorite_restaurants
    }
    
    return render(request=request, template_name="gfgauth/profile.html", context=context)


@login_required
def toggle_favorite(request, business_id):
    try:
        business = Business.objects.get(business_id=business_id)
        user = request.user
        
        if business in user.favourite_restaurants.all():
            user.favourite_restaurants.remove(business)
            is_favorite = False
        else:
            user.favourite_restaurants.add(business)
            is_favorite = True
            
        return JsonResponse({
            'status': 'success',
            'is_favorite': is_favorite
        })
    except Business.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Business not found'
        }, status=404)
# views.py
@login_required
def favorite_restaurants(request):
    favorites = request.user.favourite_restaurants.all()
    return render(request, 'favorite_restaurants.html', {
        'favorites': favorites
    })