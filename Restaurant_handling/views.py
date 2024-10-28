from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.models import Business
from django.utils import timezone
from .decorators import business_required
from .forms import DishForm, ReservationForm
from .models import Dish, Reservation

@business_required
def restaurant_dashboard(request):
    return render(request, 'Restaurant_handling/restaurant_dashboard.html')

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
        form = DishForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            try:
                dish = form.save(commit=False)
                # Get the business associated with the user
                business = Business.objects.get(business_owner=request.user)
                # Set the business_id field
                dish.business_id = business
                dish.save()
                print(f"Dish saved successfully with business_id: {business.business_id}")
                return redirect(restaurant_menu)
            except Business.DoesNotExist:
                print("No business found for user:", request.user)
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                print("Error saving dish:", str(e))
                messages.error(request, f"Error saving dish: {str(e)}")
    else:
        form = DishForm(instance=dish)
    return render(request, 'Restaurant_handling/edit_dish.html', {'form': form , 'dish': dish})

@business_required
def delete_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    dish.delete()
    return redirect(restaurant_menu) #Redirect to the restaurant menu page


@business_required
def restaurant_profile(request):
    return render(request, 'Restaurant_handling/restaurant_profile.html')

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

def reservation(request, business_id):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                reservation = form.save(commit=False)
                business = Business.objects.get(business_id=business_id)
                reservation.business_id = business
                reservation.user_id = request.user
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


"""def upcoming_reservations(request, business_id):
    try:
        business = Business.objects.get(id=business_id)
        current_datetime = timezone.now()
        
        # Get all reservations for this business
        upcoming = Reservation.objects.filter(
            business_id=business,
            models.Q(reservation_date__gt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__gt=current_datetime.time()
            )
        ).order_by('reservation_date', 'reservation_time')
        
        past = Reservation.objects.filter(
            business_id=business,
            models.Q(reservation_date__lt=current_datetime.date()) |
            models.Q(
                reservation_date=current_datetime.date(),
                reservation_time__lte=current_datetime.time()
            )
        ).order_by('-reservation_date', '-reservation_time')
        
        context = {
            'upcoming_reservations': upcoming,
            'past_reservations': past,
            'business': business
        }
        return render(request, 'upcoming_reservations.html', context)
    
    except Business.DoesNotExist:
        messages.error(request, "Business not found")
        return redirect('home') """
