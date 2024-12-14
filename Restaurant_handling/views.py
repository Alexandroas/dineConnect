from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.decorators import regular_user_or_guest
from gfgauth.forms import BusinessUpdateForm, UserUpdateForm
from gfgauth.models import Business, CustomUser, businessHours, get_business_hours
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
    """
    View to handle the addition of a new dish by a business owner.

    This view requires the user to be authenticated as a business owner.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the 'add_dish' template with the dish form and business context.
        If the form is successfully submitted and valid, redirects to the 'add_dish' view.

    Raises:
        Business.DoesNotExist: If no business is associated with the current user.
        Exception: For any other errors that occur during the dish saving process.

    Flow:
        1. Retrieves the business associated with the current user.
        2. If the request method is POST, processes the submitted form.
        3. Validates the form and attempts to save the dish.
        4. Sets the business_id for the dish and saves it.
        5. Adds any allergens to the dish if provided.
        6. Displays success or error messages based on the outcome.
        7. If the request method is not POST, initializes an empty form.
        8. Renders the 'add_dish' template with the form and business context.
    """
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
                if form.cleaned_data.get('allergens'):
                    dish.allergens.add(*form.cleaned_data['allergens'])
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
    """
    View to handle the editing of a dish.
    This view allows a business owner to edit the details of a dish. It retrieves the dish
    based on the provided dish_id and ensures that the dish belongs to the business associated
    with the current user. The view supports both GET and POST requests.
    GET:
    - Renders the edit dish form with the current details of the dish.
    POST:
    - Processes the submitted form data to update the dish.
    - Validates the form and saves the updated dish details.
    - Updates the allergens associated with the dish.
    - Displays success or error messages based on the outcome.
    Args:
        request (HttpRequest): The HTTP request object.
        dish_id (int, optional): The ID of the dish to be edited. Defaults to None.
    Returns:
        HttpResponse: The rendered edit dish page or a redirect to the restaurant menu page.
    """
    dish = get_object_or_404(Dish, dish_id=dish_id)
    business = Business.objects.get(business_owner=request.user)
    
    if request.method == 'POST':
        form = DishUpdateForm(request.POST, request.FILES, instance=dish)
        if form.is_valid():
            try:
                dish = form.save(commit=False)
                # Get the business associated with the user
                business = Business.objects.get(business_owner=request.user)
                # Set the business_id field
                dish.business_id = business
                # The is_available field will be handled automatically by form.clean_is_available()
                dish.save()
                
                dish.allergens.clear()
                if form.cleaned_data.get('allergens'):
                    dish.allergens.add(*form.cleaned_data['allergens'])
                    
                messages.success(request, 'Dish updated successfully!')
                return redirect('Restaurant_handling:restaurant_menu')
            except Business.DoesNotExist:
                messages.error(request, "Error: No business associated with this account")
            except Exception as e:
                messages.error(request, f"Error saving dish: {str(e)}")
    else:
        # Set initial value for is_available based on the current dish state
        form = DishUpdateForm(instance=dish, initial={'is_available': dish.is_available})
    
    return render(request, 'Restaurant_handling/edit_dish.html', {
        'form': form,
        'dish': dish,
        'business': business,
        'current_allergens': dish.allergens.all()
    })

@business_required
def delete_dish(request, dish_id=None):
    dish = get_object_or_404(Dish, dish_id=dish_id)
    dish.delete()
    messages.success(request, 'Dish deleted successfully!')
    return redirect('Restaurant_handling:restaurant_menu') #Redirect to the restaurant menu page

@business_required
def restaurant_profile(request):
    """
    Handles the restaurant profile view for the logged-in business owner.
    This view allows the business owner to view and update their profile information.
    It handles both GET and POST requests. On a GET request, it displays the current
    profile information. On a POST request, it processes the submitted forms to update
    the profile information.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered restaurant profile page or a redirect to the home page
                      if no business profile is found.
    Raises:
        Business.DoesNotExist: If no business profile is found for the logged-in user.
    """
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

@regular_user_or_guest
def restaurant_detail(request, business_id):
    """
    View function to display the details of a specific restaurant, including its dishes, reviews, and business hours.
    Handles review submission if the user is authenticated and has a confirmed reservation.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business to display.
    Returns:
        HttpResponse: The rendered restaurant detail page with context data.
    Context:
        business (Business): The business object for the given business_id.
        dishes (QuerySet): A queryset of dishes associated with the business, ordered by dish type name.
        reviews (QuerySet): A queryset of reviews associated with the business.
        page_obj (Page): A paginator page object containing the reviews for the current page.
        has_reviewed (bool): Indicates if the authenticated user has already reviewed the business.
        has_confirmed_reservation (bool): Indicates if the authenticated user has a confirmed reservation.
        business_hours (dict): A dictionary containing the business hours of the restaurant.
        form (ReviewForm, optional): The review form if the user is authenticated and hasn't reviewed the business.
    Raises:
        Http404: If the business with the given business_id does not exist.
    """
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business).order_by('dish_type__dish_type_name')
    reviews = Review.objects.filter(business_id=business)
    form = None
    existing_review = None
    has_confirmed_reservation = False  # Default value
    
    business_hours = get_business_hours(business)
   
    if request.user.is_authenticated:
        # Check if user has already reviewed
        existing_review = Review.objects.filter(
            business_id=business,
            user_id=request.user
        ).first()
        
        # Check for confirmed reservation only if user is authenticated
        has_confirmed_reservation = Reservation.objects.filter(
            business_id=business,
            user_id=request.user,
            reservation_status='Completed'
        ).exists()
       
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to submit a review.')
            return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
            
        if existing_review:
            messages.error(request, 'You have already reviewed this restaurant.')
            return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
            
        if not has_confirmed_reservation:
            messages.error(request, 'You must have a completed reservation to review this restaurant.')
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
        if request.user.is_authenticated and not existing_review:  # Only show form if user hasn't reviewed
            form = ReviewForm()
            
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
   
    context = {
        'business': business,
        'dishes': dishes,
        'reviews': reviews,
        'page_obj': page_obj,
        'has_reviewed': existing_review is not None,  # Simplified this check
        'has_confirmed_reservation': has_confirmed_reservation,
        'business_hours': business_hours
    }
   
    if form is not None:
        context['form'] = form
    return render(request, 'Restaurant_handling/restaurant_detail.html', context)

@business_required
def restaurant_home(request):
    """
    View function for the restaurant home page.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered restaurant home page.
    Retrieves the business associated with the current user, gathers reservation statistics,
    business hours by day, and recent reviews. Determines if the business is currently open.
    Passes this data to the 'Restaurant_handling/restaurant_home.html' template for rendering.
    Context:
        business (Business): The business object associated with the current user.
        hours_by_day (dict): A dictionary mapping day names to business hours.
        stats (dict): Reservation statistics for the business.
        is_open (bool): Whether the business is currently open.
        recent_reviews (QuerySet): A queryset of the most recent reviews for the business.
    """
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
    recent_reviews = Review.objects.filter(business_id=business)\
        .select_related('user_id')\
        .order_by('-review_id')[:5]
    context = {
        'business': business,
        'hours_by_day': hours_by_day,
        'stats': stats,
        'is_open': is_open,
        'recent_reviews': recent_reviews
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
    """
    View function to display customer details and statistics for a specific user at a specific business.
    Args:
        request (HttpRequest): The HTTP request object.
        user_id (int): The ID of the user whose details are to be displayed.
    Returns:
        HttpResponse: The rendered HTML page displaying the customer's details and statistics.
    The function performs the following tasks:
    1. Retrieves the user object based on the provided user_id.
    2. Retrieves the business associated with the current logged-in user.
    3. Fetches all reservations for the specified user at the current business, ordered by reservation date and time.
    4. Calculates various statistics related to the user's reservations, including:
        - Total number of visits.
        - Number of confirmed, pending, and cancelled reservations.
        - Top 5 favorite dishes based on order count.
        - Total amount spent on completed payments.
        - Average party size for reservations.
        - Most common reservation time and day.
        - Date and time of the last confirmed visit.
        - Whether the business is a favorite of the user.
        - Count of reservations with special requests.
    5. Prepares the context dictionary with the user, reservations, statistics, and business information.
    6. Renders the 'Restaurant_handling/customer_details.html' template with the context data.
    """
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
@regular_user_or_guest
def review_restaurant(request, business_id, reservation_id):
    """
    Handles the review submission for a restaurant by a user.

    This view function ensures that the user submitting the review is the same user who made the reservation.
    If the user is not authorized, an error message is displayed and the user is redirected to the restaurant detail page.
    If the user is authorized and the request method is POST, the review form is validated and saved.
    If the form is valid, the review is saved and a success message is displayed.
    If the request method is GET, an empty review form is rendered.

    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business being reviewed.
        reservation_id (int): The ID of the reservation associated with the review.

    Returns:
        HttpResponse: The response object containing the rendered template or a redirect.
"""
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
    """
    Handles the settings view for the logged-in business owner.
    This view allows the business owner to view and update their business settings.
    It handles both GET and POST requests. On a GET request, it displays the current
    settings information. On a POST request, it processes the submitted forms to update
    the settings information.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        HttpResponse: The rendered settings page or a redirect to the home page
                      if no business profile is found.
    Raises:
        Business.DoesNotExist: If no business profile is found for the logged-in user.
    """
    try:
        business = Business.objects.get(business_owner=request.user)
        return render(request, 'Restaurant_handling/settings.html', {'business': business})
    except Business.DoesNotExist:
        messages.error(request, "No business profile found.")
        return redirect('home')