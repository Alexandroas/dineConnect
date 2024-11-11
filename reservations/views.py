from django.shortcuts import render
from main.utils import send_reservation_email, send_cancellation_email, send_initial_res_confirmation_email, send_reservation_email_business
from notifications.utils import create_notification
from Restaurant_handling.decorators import business_required, login_required
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

@login_required
def make_reservation(request, business_id):
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
                
                # Get the day of the week for the reservation
                reservation_day = reservation.reservation_date.strftime('%A')
                business_hours_for_day = business_hours.get(reservation_day)
                
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
                except ValueError as e:
                    messages.error(request, 'Invalid business hours format.')
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
    View to display upcoming reservations for a business.
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
def cancel_reservation(request, business_id, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id,
                                  business_id=business_id)
    reservation.reservation_status = 'Cancelled'
    reservation.save()
    messages.success(request, 'Reservation canceled successfully!')
    send_cancellation_email(reservation.user_id, reservation)
    notification_message = f"The business {reservation.business_id} has cancelled your reservation on {reservation.reservation_date} at time, {reservation.reservation_time}."
    create_notification(reservation.user_id, notification_message)
    context = {
        'business': reservation.business_id,
        'reservation': reservation
    }
    return render(request, 'reservations/upcoming_reservations.html', context)
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
    context = {
        'business': reservation.business_id,
        'reservation': reservation
    }
    return render(request, 'reservations/upcoming_reservations.html', context)