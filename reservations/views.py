from django.shortcuts import render
from main.utils import send_reservation_email, send_cancellation_email, send_initial_res_confirmation_email, send_reservation_email_business
from notifications.utils import create_notification
from Restaurant_handling.decorators import business_required, login_required
from reservations.forms import ReservationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from gfgauth.models import Business
from Restaurant_handling.models import Dish
from .models import Reservation
from django.core.paginator import Paginator
from django.utils import timezone

@login_required
def make_reservation(request, business_id):
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business).order_by('dish_type__dish_type_name')
   
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                # Create reservation but don't save to DB yet
                reservation = form.save(commit=False)
                reservation.business_id = business
                reservation.user_id = request.user
                reservation.reservation_status = 'Pending'  # Add status
                print("business opening time", business.opening_time)
                print("business closing time", business.closing_time)
                if reservation.reservation_date < timezone.now().date():
                    messages.error(request, 'Reservation time cannot be in the past.')
                    return redirect('reservations:restaurant_reservation', business_id=business_id)
                # Save the reservation first
                else:
                    reservation.save()
                    
                # Handle selected dishes
                selected_dishes = request.POST.getlist('selected_dishes')
                if selected_dishes:
                    dishes_to_add = Dish.objects.filter(dish_id__in=selected_dishes)
                    reservation.dish_id.add(*dishes_to_add)
                    
                    # Calculate total amount
                    total_amount = sum(dish.dish_cost for dish in dishes_to_add)
                    
                    if total_amount > 0:
                        # Redirect to payment if there are dishes selected
                        return redirect('payments:payment', reservation_id=reservation.reservation_id)
                    
                # If no dishes selected, just send confirmation email
                if reservation:
                    send_initial_res_confirmation_email(request.user, reservation)
                    send_reservation_email_business(business, reservation)
                    notification_message = f"New reservation from {request.user.get_full_name()} for {reservation.reservation_party_size} people on {reservation.reservation_date} at {reservation.reservation_time}."
                    create_notification(business.business_owner, notification_message)
                messages.success(request, 'Your reservation has been saved!')
                return redirect('Restaurant_handling:restaurant_detail', business_id=business_id)
               
            except Exception as e:
                print("Error saving reservation:", str(e))
                messages.error(request, f"Error saving reservation: {str(e)}")
                # If error occurs, try to delete the reservation if it was created
                if 'reservation' in locals() and reservation.reservation_id:
                    reservation.delete()
    else:
        form = ReservationForm()
   
    return render(request, 'reservations/reservation.html', {
        'form': form,
        'business': business,
        'dishes': dishes
    })

from django.template.loader import get_template

@business_required
def upcoming_reservations(request, business_id):
    """
    View to display upcoming reservations for a business.
    """
    print("1. View started")  # Debug print
    try:
        business = get_object_or_404(Business, business_id=business_id)
        print(f"2. Business found: {business}")  # Debug print
       
        # Get filter parameters
        date_filter = request.GET.get('date')
        status_filter = request.GET.get('status')
        print(f"3. Filters: date={date_filter}, status={status_filter}")  # Debug print
       
        # Use the class method instead of repeating the filter logic
        reservations = Reservation.upcoming_reservations().filter(business_id=business)
        print(f"4. Reservations query created")  # Debug print
       
        # Calculate counts
        total_upcoming = reservations.count()
        today_count = reservations.filter(
            reservation_date=timezone.now().date()
        ).count()
        print(f"5. Counts: total={total_upcoming}, today={today_count}")  # Debug print
       
        # Pagination
        paginator = Paginator(reservations, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        print("6. Pagination complete")  # Debug print
       
        context = {
            'business': business,
            'page_obj': page_obj,
            'total_upcoming': total_upcoming,
            'today_count': today_count,
            'current_date': timezone.now().date(),
            'date_filter': date_filter,
            'status_filter': status_filter,
        }
        print("7. Context created:", context)  # Debug print
       
        try:
            print("8. Attempting to render template")  # Debug print
            response = render(
                request,
                'reservations/upcoming_reservations.html',
                context
            )
            print("9. Template rendered successfully")  # Debug print
            return response
        except Exception as template_error:
            print(f"Template error: {str(template_error)}")  # Debug print
            raise
       
    except Exception as e:
        print(f"Main error: {str(e)}")  # Debug print
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
    messages.success(request, 'Reservation confirmed successfully!')
    context = {
        'business': reservation.business_id,
        'reservation': reservation
    }
    return render(request, 'reservations/upcoming_reservations.html', context)