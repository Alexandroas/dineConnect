from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.forms import BusinessUpdateForm, UserUpdateForm  # Import your existing form
from gfgauth.models import Business
from .decorators import business_required, login_required
from .forms import DishForm, ReservationForm, DishUpdateForm
from .models import Dish
from main.utils import send_reservation_email
@business_required
def restaurant_dashboard(request):
    try:
        business = Business.objects.get(business_owner=request.user)
        context = {
            'business': business,
        }
        return render(request, 'Restaurant_handling/restaurant_dashboard.html', context)
    except Business.DoesNotExist:
        messages.error(request, "No business profile found.")
        return redirect('home')

@business_required
def add_dish(request):
    if request.method == 'POST':
        form = DishForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                dish = form.save(commit=False)
                # Get the business associated with the user
                business = Business.objects.get(business_owner=request.user)
                # Set the business_id field
                dish.business_id = business  # or dish.BusinessID depending on your model
                dish.save()
                print(f"Dish saved successfully with business_id: {business.business_id}")
                return redirect('add_dish')
            except Business.DoesNotExist:
                print("No business found for user:", request.user)
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                print("Error saving dish:", str(e))
                messages.error(request, f"Error saving dish: {str(e)}")
    else:
        form = DishForm()
    return render(request, 'Restaurant_handling/add_dish.html', {'form': form})

@business_required
def edit_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    if request.method == 'POST':
        form = DishUpdateForm(request.POST, request.FILES, instance=dish)  # Changed to DishUpdateForm
        if form.is_valid():
            try:
                dish = form.save(commit=False)
                # Get the business associated with the user
                business = Business.objects.get(business_owner=request.user)
                # Set the business_id field
                dish.business_id = business
                # Convert is_available string to boolean if using ChoiceField
                dish.is_available = form.cleaned_data['is_available'] == 'True'
                dish.save()
                messages.success(request, 'Dish updated successfully!')
                return redirect('restaurant_menu')
            except Business.DoesNotExist:
                print("No business found for user:", request.user)
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                print("Error saving dish:", str(e))
                messages.error(request, f"Error saving dish: {str(e)}")
    else:
        form = DishUpdateForm(instance=dish)  # Changed to DishUpdateForm
        
    return render(request, 'Restaurant_handling/edit_dish.html', {
        'form': form,
        'dish': dish
    })

@business_required
def delete_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    dish.delete()
    return redirect(restaurant_menu) #Redirect to the restaurant menu page

@business_required
def restaurant_profile(request):
    try:
        business = Business.objects.get(business_owner=request.user)
        
        if request.method == 'POST':
            user_form = UserUpdateForm(request.POST, instance=request.user)
            business_form = BusinessUpdateForm(request.POST, request.FILES, instance=business)
            
            if user_form.is_valid() and business_form.is_valid():
                user_form.save()
                business_form.save()
                messages.success(request, f'Your profile has been updated successfully!')
                return redirect("restaurant_profile")
            else:
                for error in list(user_form.errors.values()) + list(business_form.errors.values()):
                    messages.error(request, error)
        else:
            user_form = UserUpdateForm(instance=request.user)
            business_form = BusinessUpdateForm(instance=business)
            
        context = {
            'business': business,
            'user_form': user_form,
            'business_form': business_form
        }
        return render(request, 'Restaurant_handling/restaurant_profile.html', context)
        
    except Business.DoesNotExist:
        messages.error(request, "No business profile found.")
        return redirect('home')

@business_required
def restaurant_profile_settings(request):
    return render(request, 'Restaurant_handling/restaurant_profile_settings.html')
#TODO: Add a 403.html file in the templates/Restaurant_handling/ directory
def permission_denied_view(request, exception):
    return render(request, 'Restaurant_handling/403.html', status=403)

@business_required
def restaurant_menu(request):
    dishes = Dish.objects.filter(business_id=request.user.business)
    return render(request, 'Restaurant_handling/registered_dishes.html', {'dishes': dishes})
def restaurant_detail(request, business_id):
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business)
    context = {
        'business': business,
        'dishes': dishes  # Add dishes to context
    }
    return render(request, 'Restaurant_handling/restaurant_detail.html', context)

@business_required
def restaurant_home(request):
    return render(request, 'Restaurant_handling/restaurant_home.html')

@login_required
def reservation(request, business_id):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save(commit=False)
                business = Business.objects.get(business_id=business_id)
                reservation.business_id = business
                reservation.user_id = request.user
                send_reservation_email(request.user, reservation)
                messages.success(request, 'Your reservation has been saved!')
                reservation.save()
                print(f"Reservation saved successfully with business_id: {business.business_id}")
                return redirect('restaurant_detail', business_id=business_id)
            except Business.DoesNotExist:
                print("No business found for user:", request.user)
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                print("Error saving reservation:", str(e))
                messages.error(request, f"Error saving reservation: {str(e)}")
    else:
        form = ReservationForm()
    return render(request, 'Restaurant_handling/reservation.html', {'form': form , 'business_id': business_id})

