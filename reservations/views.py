from django.shortcuts import render
from gfgauth.decorators import regular_user_or_guest
from main.utils import send_reservation_email, send_cancellation_email, send_initial_res_confirmation_email, send_reservation_email_business, send_completion_email
from notifications.utils import create_notification
from Restaurant_handling.decorators import business_required, login_required
from payments.models import Payment
from reservations.forms import ReservationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.models import Business, get_business_hours
from Restaurant_handling.models import Dish
from .models import Reservation
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime
import stripe # type: ignore
from django.conf import settings
from django.db import models

@login_required
@regular_user_or_guest
def make_reservation(request, business_id):
    """
    Handles the creation of a reservation for a given business.
    Args:
        request (HttpRequest): The HTTP request object containing POST data for the reservation.
        business_id (int): The ID of the business for which the reservation is being made.
    Returns:
        HttpResponse: Renders the reservation form page or redirects to appropriate pages based on the reservation status.
    The function performs the following steps:
    1. Retrieves the business object and its associated dishes and business hours.
    2. Checks if the business is open.
    3. If the request method is POST, it processes the reservation form:
        - Validates the form data.
        - Checks if the reservation date is in the past.
        - Checks if the party size exceeds the business's maximum table capacity.
        - Checks if the reservation time is within the business hours for the selected day.
        - Saves the reservation and handles selected dishes.
        - If dishes are selected, redirects to the payment page.
        - If no dishes are selected, sends confirmation emails and creates a notification.
    4. If the request method is not POST, it initializes an empty reservation form.
    5. Renders the reservation form page with the context data.
    """
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business).order_by('dish_type__dish_type_name')
    business_hours = get_business_hours(business)
   
    print("business hours", business_hours)
    is_open = business.is_open()
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                # Create reservation but don't save to DB yet
                reservation = form.save(commit=False)
                reservation.business_id = business
                reservation.user_id = request.user
                reservation.reservation_status = 'Pending'
                
                # Check if date is in the past
                if reservation.reservation_date < timezone.now().date():
                    messages.error(request, 'Reservation time cannot be in the past.')
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                    
                if reservation.reservation_party_size > business.business_max_table_capacity:
                    messages.error(request, f"Party size cannot exceed the restaurant max party size of: {business.business_max_table_capacity}.")
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                
                # Get the day of the week for the reservation
                reservation_day = reservation.reservation_date.strftime('%A')
                business_hours_for_day = business_hours.get(reservation_day)
                
                # Check if business hours exist for this day
                if not business_hours_for_day:
                    messages.error(request, f'Sorry, business hours are not set for {reservation_day}s.')
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                
                if business_hours_for_day == 'Closed':
                    messages.error(request, f'Sorry, we are closed on {reservation_day}s.')
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                
                # Parse business hours string to get opening and closing times
                try:
                    opening_time_str, closing_time_str = business_hours_for_day.split(' - ')
                    opening_time = datetime.strptime(opening_time_str, '%H:%M').time()
                    closing_time = datetime.strptime(closing_time_str, '%H:%M').time()
                    
                    # Check if reservation time is within business hours
                    if reservation.reservation_time < opening_time or reservation.reservation_time > closing_time:
                        messages.error(request, f'Reservation time must be between {opening_time_str} and {closing_time_str}.')
                        return redirect('reservations:restaurant_reservation', business_id=business_id)
                except (ValueError, AttributeError) as e:
                    messages.error(request, f'Invalid business hours format for {reservation_day}.')
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                
                # If all checks pass, save the reservation
                reservation.save()
                
                # Handle selected dishes
                selected_dishes = request.POST.getlist('selected_dishes')
                if selected_dishes:
                    dishes_to_add = Dish.objects.filter(dish_id__in=selected_dishes)
                    reservation.dish_id.add(*dishes_to_add)
                    
                    # Calculate total amount
                    total_amount = sum(dish.dish_cost for dish in dishes_to_add)
                    
                    if total_amount > 0:
                        return redirect('payments:payment', reservation_id=reservation.reservation_id)
                
                # If no dishes selected, send confirmation emails
                send_initial_res_confirmation_email(request.user, reservation)
                send_reservation_email_business(business, reservation)
                notification_message = f"New reservation from {request.user.get_full_name()} for {reservation.reservation_party_size} people on {reservation.reservation_date} at {reservation.reservation_time}."
                create_notification(business.business_owner, notification_message)
                messages.success(request, 'Your reservation has been saved!')
                return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
                
            except Exception as e:
                print("Error saving reservation:", str(e))
                messages.error(request, f"Error saving reservation: {str(e)}")
                if 'reservation' in locals() and reservation.reservation_id:
                    reservation.delete()
    else:
        form = ReservationForm()
    
    context = {
        'form': form,
        'business': business,
        'dishes': dishes,
        'business_hours': business_hours,
        'is_open': is_open
    }
    
    return render(request, 'reservations/reservation.html', context)

@business_required
def upcoming_reservations(request, business_id):
    """
    This view handles the following functionalities:
        - Retrieves the business object based on the provided business_id.
        - Fetches upcoming reservations for the business.
        - Applies optional filters for date and status.
        - Orders the reservations by date and time.
        - Calculates the total number of upcoming reservations and the count for today's reservations.
        - Implements pagination for the reservations list.
        - Renders the 'upcoming_reservations.html' template with the context data.
        Parameters:
            request (HttpRequest): The HTTP request object.
            business_id (int): The ID of the business for which to display reservations.
        Returns:
            HttpResponse: The rendered HTML page displaying the upcoming reservations.
        Raises:
            Http404: If the business object is not found.
            Exception: For any other errors that occur during the view execution.
    """
    try:
        business = get_object_or_404(Business, business_id=business_id)
        
        # Get base queryset
        reservations = Reservation.upcoming_reservations().filter(business_id=business)
        
        # Get filter parameters
        date_filter = request.GET.get('date')
        status_filter = request.GET.get('status')
        
        # Apply date filter if provided
        if date_filter:
            try:
                # Convert string date to datetime object
                filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
                print(f"Filtering by date: {filter_date}")  # Debug print
                reservations = reservations.filter(reservation_date=filter_date)
            except ValueError as e:
                print(f"Date conversion error: {e}")  # Debug print
                messages.error(request, "Invalid date format")
        
        # Apply status filter if provided
        if status_filter and status_filter != 'all':
            print(f"Filtering by status: {status_filter}")  # Debug print
            reservations = reservations.filter(reservation_status=status_filter)
        
        # Debug prints
        print(f"Query before evaluation: {reservations.query}")
        
        # Order results
        reservations = reservations.order_by('reservation_date', 'reservation_time')
        
        # Calculate counts
        total_upcoming = reservations.count()
        today_count = reservations.filter(
            reservation_date=timezone.now().date()
        ).count()
        
        # Pagination
        paginator = Paginator(reservations, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'business': business,
            'page_obj': page_obj,
            'total_upcoming': total_upcoming,
            'today_count': today_count,
            'current_date': timezone.now().date(),
            'date_filter': date_filter,
            'status_filter': status_filter,
            # Add available statuses to context for the dropdown
            'available_statuses': ['Pending', 'Confirmed', 'Cancelled']
        }
        
        return render(
            request,
            'reservations/upcoming_reservations.html',
            context
        )
        
    except Exception as e:
        print(f"Error in view: {str(e)}")
        messages.error(request, f"An error occurred while loading reservations: {str(e)}")
        return redirect('Restaurant_handling:restaurant_home')
    
@business_required
def reservation_details(request, business_id, reservation_id):
    """
    View to display details of a reservation.
    """
    business = get_object_or_404(Business, business_id=business_id)
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id,
                                  business_id=business)
   
    # Calculate total amount if there are dishes
    total_amount = sum(dish.dish_cost for dish in reservation.dish_id.all())
   
    context = {
        'business': business,
        'reservation': reservation,
        'total_amount': total_amount
    }
   
    return render(request, 'reservations/reservation_details.html', context)

@business_required
def past_reservations(request, business_id):
    """
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business for which to display past reservations.
    Returns:
        HttpResponse: The rendered HTML page displaying past reservations.
    This view performs the following steps:
    1. Retrieves the business object using the provided business_id.
    2. Fetches past reservations for the business, either completed or with dates in the past.
    3. Applies optional filters for reservation date and status based on query parameters.
    4. Orders the reservations by most recent date and time.
    5. Calculates statistics for total past reservations, completed reservations, and cancelled reservations.
    6. Paginates the results to display 20 reservations per page.
    7. Renders the 'reservations/past_reservations.html' template with the context data.
    If an error occurs during processing, an error message is displayed and the user is redirected to the restaurant home page.
    """
    try:
        business = get_object_or_404(Business, business_id=business_id)
        
        # Get base queryset of past reservations
        # Either completed or date is in the past
        current_date = timezone.now().date()
        reservations = Reservation.objects.filter(
            business_id=business
        ).filter(
            # Get completed reservations or reservations with past dates
            models.Q(reservation_status='Completed') |
            models.Q(reservation_date__lt=current_date)
        )
        
        # Get filter parameters
        date_filter = request.GET.get('date')
        status_filter = request.GET.get('status')
        
        # Apply date filter if provided
        if date_filter:
            try:
                filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
                reservations = reservations.filter(reservation_date=filter_date)
            except ValueError:
                messages.error(request, "Invalid date format")
        
        # Apply status filter if provided
        if status_filter and status_filter != 'all':
            reservations = reservations.filter(reservation_status=status_filter)
        
        # Order results by most recent first
        reservations = reservations.order_by('-reservation_date', '-reservation_time')
        
        # Calculate statistics
        total_past = reservations.count()
        completed_count = reservations.filter(reservation_status='Completed').count()
        cancelled_count = reservations.filter(reservation_status='Cancelled').count()
        
        # Pagination
        paginator = Paginator(reservations, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        context = {
            'business': business,
            'page_obj': page_obj,
            'total_past': total_past,
            'completed_count': completed_count,
            'cancelled_count': cancelled_count,
            'date_filter': date_filter,
            'status_filter': status_filter,
            'available_statuses': ['Completed', 'Cancelled']
        }
        
        return render(
            request,
            'reservations/past_reservations.html',
            context
        )
        
    except Exception as e:
        print(f"Error in view: {str(e)}")
        messages.error(request, f"An error occurred while loading past reservations: {str(e)}")
        return redirect('Restaurant_handling:restaurant_home')

@business_required
def cancel_reservation(request, business_id, reservation_id):
    """
    Cancel a reservation for a business.
    This view handles the cancellation of a reservation for a specific business. It performs the following steps:
    1. Retrieves the reservation object based on the provided reservation_id and business_id.
    2. Checks for any associated payments with the reservation.
    3. If a payment with status 'Pending' or 'Succeeded' is found, it processes a refund using Stripe.
    4. Updates the payment status to 'Refunded' if the refund is successful.
    5. If no successful payment is found, it logs the statuses of other payments.
    6. Updates the reservation status to 'Cancelled'.
    7. Sends a cancellation email to the user.
    8. Creates a notification for the user about the cancellation.
    9. Redirects to the upcoming reservations page for the business.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business.
        reservation_id (int): The ID of the reservation to be canceled.
    Returns:
        HttpResponseRedirect: Redirects to the upcoming reservations page for the business.
"""
    reservation = get_object_or_404(Reservation,
                                  reservation_id=reservation_id,
                                  business_id=business_id)
    
    print(f"DEBUG: Cancelling reservation {reservation_id} for business {business_id}")
    
    # Check for payments
    payments = Payment.objects.filter(reservation=reservation)
    print(f"DEBUG: Found {payments.count()} payments for this reservation")
    
    # Get the associated payment
    try:
        payment = Payment.objects.get(
        reservation=reservation,
        status__in=['Pending', 'Succeeded']
    )
        print(f"DEBUG: Found payment {payment.id} with status {payment.status}")
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_intent_id
        )
        
        payment.status = 'Refunded'
        payment.save()
        
        messages.success(request, 'Reservation canceled and payment refunded successfully!')
        
    except Payment.DoesNotExist:
        print(f"DEBUG: No successful payment found for reservation {reservation_id}")
        # Check if there are any payments in other statuses
        other_payments = Payment.objects.filter(reservation=reservation)
        for p in other_payments:
            print(f"DEBUG: Found payment {p.id} with status: {p.status}")
        messages.success(request, 'Reservation canceled successfully!')
    except stripe.error.StripeError as e:
        print(f"DEBUG: Stripe error: {str(e)}")
        messages.warning(request, f'Reservation canceled but there was an issue processing the refund: {str(e)}')
    
    # Continue with rest of your code...
    reservation.reservation_status = 'Cancelled'
    reservation.save()
    
    send_cancellation_email(reservation.user_id, reservation)
    notification_message = f"The business {reservation.business_id} has cancelled your reservation on {reservation.reservation_date} at time, {reservation.reservation_time}."
    create_notification(reservation.user_id, notification_message)
    
    return redirect('reservations:upcoming_reservations', business_id=business_id)


@business_required
def confirm_reservation(request, business_id, reservation_id):
    reservation = get_object_or_404(Reservation, reservation_id=reservation_id, business_id=business_id)
    if reservation.reservation_status == 'Confirmed':
        messages.error(request, 'Reservation already confirmed!')
        return redirect('reservations:upcoming_reservations', business_id=business_id)
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id,
                                  business_id=business_id)
    reservation.reservation_status = 'Confirmed'
    reservation.save()
    send_reservation_email(reservation.user_id, reservation)
    notification_message = f"The business {reservation.business_id} has confirmed your reservation on {reservation.reservation_date} at time, {reservation.reservation_time}."
    create_notification(reservation.user_id, notification_message)
    messages.success(request, 'Reservation confirmed successfully!')
    return redirect('reservations:upcoming_reservations', business_id=business_id)

@business_required
def complete_reservation(request, business_id, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id,
                                  business_id=business_id)
    reservation.reservation_status = 'Completed'
    reservation.save()
    send_completion_email(reservation.user_id, reservation)
    messages.success(request, 'Reservation completed successfully!')
    return redirect('reservations:upcoming_reservations', business_id=business_id)