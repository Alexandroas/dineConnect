from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from Restaurant_handling.decorators import business_required
from gfgauth.decorators import regular_user_or_guest
from main.utils import send_reservation_email
from notifications.utils import create_notification
import stripe  # type: ignore
from reservations.models import Reservation
from gfgauth.models import Business
from django.views.decorators.http import require_POST
import json
from django.http import JsonResponse
from .models import Payment
from django.urls import reverse
from dineConnect_project import settings
from django.db import models
from django.db.models import Sum, Count
from django.core.paginator import Paginator
# Create your views here.
def payment_view(request, reservation_id):
    """
    Handles the payment process for a reservation.
    This view performs the following steps:
    1. Retrieves the reservation and verifies it belongs to the current user.
    2. Calculates the total amount from the selected dishes in the reservation.
    3. Checks if there is an existing successful payment for the reservation.
    4. If a POST request is made, it creates a Stripe payment intent and renders the payment page.
    5. If a GET request is made, it renders the payment form.
    Args:
        request (HttpRequest): The HTTP request object.
        reservation_id (int): The ID of the reservation to be paid for.
    Returns:
        HttpResponse: The response object containing the rendered payment page or a redirect.
    """
    # Get the reservation and verify it belongs to the current user
    reservation = get_object_or_404(
        Reservation,
        reservation_id=reservation_id,
        user_id=request.user
    )
   
    # Calculate total amount from selected dishes
    total_amount = sum(dish.dish_cost for dish in reservation.dish_id.all())
   
    # Ensure there's no existing successful payment for this reservation
    existing_payment = Payment.objects.filter(
        reservation=reservation,
        status='succeeded'
    ).first()
   
    if existing_payment:
        messages.warning(request, "This reservation has already been paid for.")
        return redirect('reservations:reservation_details', 
                       business_id=reservation.business_id.business_id,
                       reservation_id=reservation_id)

    if request.method == 'POST':
        try:
            stripe.api_key = settings.STRIPE_SECRET_KEY
           
            # Create Stripe payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'reservation_id': reservation.reservation_id,
                    'user_email': request.user.email,
                    'business_id': reservation.business_id.business_id
                },
                description=f"Reservation #{reservation.reservation_id} at {reservation.business_id.business_name}"
            )
            return render(request, 'payments/payment.html', {
                'reservation': reservation,
                'total_amount': total_amount,
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
            })
           
        except stripe.error.StripeError as e:
            # Handle Stripe-specific errors
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('reservations:reservation_details', 
                          business_id=reservation.business_id.business_id,
                          reservation_id=reservation_id)
           
        except Exception as e:
            # Handle other unexpected errors
            messages.error(request, "An unexpected error occurred. Please try again.")
            return redirect('reservations:reservation_details', 
                          business_id=reservation.business_id.business_id,
                          reservation_id=reservation_id)
   
    # GET request - show payment form
    context = {
        'reservation': reservation,
        'total_amount': total_amount,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
        'business_name': reservation.business_id.business_name
    }
   
    return render(request, 'payments/payment.html', context)

def payment_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id, 
                                  user_id=request.user)
    
    # Update reservation status
    reservation.reservation_status = 'Confirmed'
    reservation.save()
    # Send confirmation email
    send_reservation_email(request.user, reservation)
    notification_message = f"New reservation from {request.user.get_full_name()} for {reservation.reservation_party_size} people on {reservation.reservation_date} at {reservation.reservation_time}."
    create_notification(reservation.business_id.business_owner, notification_message)
    messages.success(request, 'Payment successful! Your reservation is confirmed.')
    return redirect('Restaurant_handling:restaurant_detail', business_id=reservation.business_id.business_id)

def payment_cancel(request, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id, 
                                  user_id=request.user)
    
    messages.warning(request, 'Payment was cancelled. Your reservation is still pending.')
    return redirect('Restaurant_handling:restaurant_detail', business_id=reservation.business_id.business_id)

@require_POST
def process_payment(request, reservation_id):
    """
    Processes a payment for a given reservation.
    Args:
        request (HttpRequest): The HTTP request object containing payment details.
        reservation_id (int): The ID of the reservation for which the payment is being processed.
    Returns:
        JsonResponse: A JSON response indicating the success or failure of the payment process.
    Raises:
        stripe.error.CardError: If there is an error with the card during the payment process.
        Exception: For any other exceptions that occur during the payment process.
    The function performs the following steps:
    1. Parses the payment details from the request body.
    2. Retrieves the reservation object based on the reservation_id and user_id.
    3. Calculates the total amount for the reservation.
    4. Creates a Stripe payment intent with the calculated amount and payment method.
    5. Creates a Payment object to record the payment details.
    6. Updates the reservation status to 'Confirmed' if the payment is successful.
    7. Sends a confirmation email to the user if the payment is successful.
    8. Returns a JSON response indicating the success or failure of the payment process.
    """
    try:
        data = json.loads(request.body)
        payment_method_id = data.get('payment_method_id')
        
        reservation = get_object_or_404(Reservation, 
                                      reservation_id=reservation_id,
                                      user_id=request.user)
        
        total_amount = sum(dish.dish_cost for dish in reservation.dish_id.all())
        
        # Create payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        intent = stripe.PaymentIntent.create(
            amount=int(total_amount * 100),  # Convert to cents
            currency='usd',
            payment_method=payment_method_id,
            confirm=True,  # Confirm the payment immediately
            return_url=request.build_absolute_uri(
                reverse('payments:payment_success', args=[reservation_id])
            ),
            metadata={
                'reservation_id': reservation.reservation_id,
                'user_email': request.user.email,
                'business_id': reservation.business_id.business_id
            }
        )
        Payment.objects.create(
            reservation=reservation,
            amount=total_amount,
            stripe_payment_intent_id=intent.id,
            user=request.user,
            business=reservation.business_id,
            status='Succeeded' if intent.status == 'Succeeded' else 'Pending' 
        )
        
        if intent.status == 'succeeded':
            # Update reservation status
            reservation.reservation_status = 'Confirmed'
            reservation.save()
            
            # Send confirmation email
            send_reservation_email(request.user, reservation)
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('payments:payment_success', args=[reservation_id])
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Payment failed.'
            })
            
    except stripe.error.CardError as e:
        return JsonResponse({
            'success': False,
            'error': e.error.message
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
@regular_user_or_guest
def payment_history(request):
    payments = Payment.objects.filter(user=request.user)
    return render(request, 'payments/payment_history.html', {'payments': payments})

@business_required
def business_payment_history(request, business_id):
    """
    View to display the payment history for a specific business.
    Args:
        request (HttpRequest): The HTTP request object.
        business_id (int): The ID of the business whose payment history is to be displayed.
    Returns:
        HttpResponse: The rendered HTML page displaying the payment history and statistics.
    The view performs the following actions:
    1. Retrieves the business object using the provided business_id.
    2. Fetches all payments related to the business, including related user and reservation data.
    3. Aggregates payment statistics such as total revenue and count of successful payments.
    4. Implements pagination to display a limited number of payments per page.
    5. Renders the 'payments/business_payment_history.html' template with the context data.
    """
    business = get_object_or_404(Business, business_id=business_id)
   
    # Get all payments for this business
    payments = Payment.objects.filter(
        business=business
    ).select_related(
        'user',
        'reservation'
    ).order_by('-created_at')
   
    # Calculate statistics using aggregation
    payment_stats = payments.aggregate(
        total_revenue=Sum('amount', filter=models.Q(status='succeeded')),
        successful_payments=Count('id', filter=models.Q(status='succeeded'))
    )
    
    # Pagination
    page_number = request.GET.get('page', 1)
    paginator = Paginator(payments, 10)  # Show 10 payments per page
    page_obj = paginator.get_page(page_number)
   
    context = {
        'payments': page_obj,  # Use page_obj instead of payments
        'business': business,
        'total_revenue': payment_stats['total_revenue'] or 0,
        'successful_payments': payment_stats['successful_payments'],
        'page_obj': page_obj,  # Add page_obj to context
    }
   
    return render(request, 'payments/business_payment_history.html', context)