from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.forms import BusinessUpdateForm, UserUpdateForm
from gfgauth.models import Business, CustomUser, businessHours
from .decorators import business_required
from .forms import DishForm, DishUpdateForm, ReviewForm
from .models import Dish, Review
from reservations.models import Reservation
from payments.models import Payment
from django.db import models
from django.core.paginator import Paginator
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
    business = Business.objects.get(business_owner=request.user)
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
                messages.success(request, 'Dish saved successfully!')
                print(f"Dish saved successfully with business_id: {business.business_id}")
                return redirect('Restaurant_handling:add_dish')
            except Business.DoesNotExist:
                print("No business found for user:", request.user)
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                print("Error saving dish:", str(e))
                messages.error(request, f"Error saving dish: {str(e)}")
    else:
        form = DishForm()
    return render(request, 'Restaurant_handling/add_dish.html', {'form': form, 'business': business})

@business_required
def edit_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    business = Business.objects.get(business_owner=request.user)
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
        'dish': dish,
        'business': business
    })

@business_required
def delete_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    dish.delete()
    messages.success(request, 'Dish deleted successfully!')
    return redirect('Restaurant_handling:restaurant_menu') #Redirect to the restaurant menu page

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
                return redirect('Restaurant_handling:restaurant_profile')
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
    # Get the business associated with the logged-in user
    business = Business.objects.filter(business_owner=request.user).first()
    dishes = Dish.objects.filter(business_id=business).order_by('dish_type__dish_type_name')
    return render(request, 'Restaurant_handling/registered_dishes.html', {
        'dishes': dishes,
        'business': business  # Add business to the context
    })


# In your views.py
def restaurant_detail(request, business_id):
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business).order_by('dish_type__dish_type_name')
    reviews = Review.objects.filter(business_id=business)
    form = None
   
    if request.user.is_authenticated:
        # Check if user has already reviewed
        existing_review = Review.objects.filter(
            business_id=business, 
            user_id=request.user
        ).first()
        
        if request.method == 'POST':
            if existing_review:
                messages.error(request, 'You have already reviewed this restaurant.')
                return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
                
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.business_id = business
                review.user_id = request.user
                review.save()
                messages.success(request, 'Review saved successfully!')
                return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
        else:
            if not existing_review:  # Only show form if user hasn't reviewed
                form = ReviewForm()

    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'business': business,
        'dishes': dishes,
        'reviews': reviews,
        'page_obj': page_obj,
        'has_reviewed': Review.objects.filter(business_id=business, user_id=request.user).exists() if request.user.is_authenticated else False
    }
   
    if form is not None:
        context['form'] = form
    return render(request, 'Restaurant_handling/restaurant_detail.html', context)

@business_required
def restaurant_home(request):
    business = get_object_or_404(Business, business_owner=request.user)
    stats = business.get_reservation_stats()
    hours_by_day = {}
    
    for day_number, day_name in businessHours.DAYS_OF_WEEK:
        hours = business.business_hours.filter(day_of_week=day_number).order_by('opening_time')
        hours_by_day[day_name] = hours
    if is_open := business.is_open():
        is_open = True
    else:
        is_open = False
    context = {
        'business': business,
        'hours_by_day': hours_by_day,
        'stats': stats,
        'is_open': is_open
    }
    return render(request, 'Restaurant_handling/restaurant_home.html', context)

@business_required
def manage_customers(request):
    business = Business.objects.get(business_owner=request.user)
    users_with_stats = business.get_reservation_users_with_stats()
    
    context = {
        'business': business,
        'customers': users_with_stats,
    }
    
    return render(request, 'Restaurant_handling/manage_customers.html', context)

@business_required
def customer_details(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    business = request.user.business
    
    # Get all reservations for this user at this business
    reservations = Reservation.objects.filter(
        user_id=user,
        business_id=business
    ).order_by('-reservation_date', '-reservation_time')
    
    # Calculate statistics
    stats = {
        'total_visits': reservations.count(),
        'confirmed_reservations': reservations.filter(reservation_status='Confirmed').count(),
        'pending_reservations': reservations.filter(reservation_status='Pending').count(),
        'cancelled_reservations': reservations.filter(reservation_status='Cancelled').count(),
        'favorite_dishes': Dish.objects.filter(
            reservation__in=reservations
        ).annotate(
            order_count=models.Count('dish_id')
        ).order_by('-order_count')[:5],
        'total_spent': Payment.objects.filter(
            reservation__in=reservations,
            status='completed'
        ).aggregate(total=models.Sum('amount'))['total'] or 0,
        'average_party_size': reservations.aggregate(
            avg=models.Avg('reservation_party_size')
        )['avg'] or 0,
        'most_common_time': reservations.exclude(
            reservation_status='Cancelled'
        ).values('reservation_time').annotate(
            count=models.Count('reservation_id')
        ).order_by('-count').first(),
        'most_common_day': reservations.exclude(
            reservation_status='Cancelled'
        ).values('reservation_date__week_day').annotate(
            count=models.Count('reservation_id')
        ).order_by('-count').first(),
        'last_visit': reservations.filter(
            reservation_status='Confirmed'
        ).first(),
        'is_favorite': business in user.favourite_restaurants.all(),
        'special_requests_count': reservations.exclude(
            reservation_special_requests__isnull=True
        ).exclude(
            reservation_special_requests__exact=''
        ).count(),
    }
    
    context = {
        'user': user,
        'reservations': reservations,
        'stats': stats,
        'business': business
    }
   
    return render(request, 'Restaurant_handling/customer_details.html', context)

@login_required
def review_restaurant(request, business_id, reservation_id):
    reservation_id = get_object_or_404(Reservation, reservation_id=reservation_id)
    user = get_object_or_404(CustomUser, id=reservation_id.user_id)
    business = get_object_or_404(Business, business_id=business_id)
    if user != request.user: # Check if the user is the same as the one who made the reservation
        messages.error(request, 'You are not authorized to review this restaurant.')
        return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
    else:
        if request.method == 'POST':
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.business_id = business
                review.user_id = request.user
                review.save()
                messages.success(request, 'Review saved successfully!')
                return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
        else:
            form = ReviewForm()
    return render(request, 'Restaurant_handling/review_restaurant.html', {'form': form, 'business': business})
    
@business_required
def settings(request):
    business = Business.objects.get(business_owner=request.user)
    
    return render(request, 'Restaurant_handling/settings.html')