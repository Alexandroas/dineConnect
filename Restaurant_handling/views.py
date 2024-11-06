from django.utils import timezone
from venv import logger
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from dineConnect_project import settings
from gfgauth.forms import BusinessUpdateForm, UserUpdateForm  # Import your existing form
from gfgauth.models import Business
from django.db.models import Q
from .decorators import business_required, login_required
from .forms import DishForm, ReservationForm, DishUpdateForm
from .models import Dish, Reservation
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
    # Get the business associated with the logged-in user
    business = Business.objects.filter(business_owner=request.user).first()
    dishes = Dish.objects.filter(business_id=business)
    return render(request, 'Restaurant_handling/registered_dishes.html', {
        'dishes': dishes,
        'business': business  # Add business to the context
    })
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
    business = get_object_or_404(Business, business_owner=request.user)
    return render(request, 'Restaurant_handling/restaurant_home.html', {'business': business})
import stripe
@login_required
def make_reservation(request, business_id):
    business = get_object_or_404(Business, business_id=business_id)
    dishes = Dish.objects.filter(business_id=business)
   
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            try:
                # Create reservation but don't save to DB yet
                reservation = form.save(commit=False)
                reservation.business_id = business
                reservation.user_id = request.user
                reservation.reservation_status = 'Pending'  # Add status
               
                # Save the reservation first
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
                        return redirect('Restaurant_handling:payment', reservation_id=reservation.reservation_id)
                    
                # If no dishes selected, just send confirmation email
                send_reservation_email(request.user, reservation)
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
   
    return render(request, 'Restaurant_handling/reservation.html', {
        'form': form,
        'business': business,
        'dishes': dishes
    })

def payment_view(request, reservation_id):
    # Get the reservation and verify it belongs to the current user
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id, 
                                  user_id=request.user)
    
    # Calculate total amount from selected dishes
    total_amount = sum(dish.dish_cost for dish in reservation.dish_id.all())
    
    if request.method == 'POST':
        try:
            # Create Stripe payment intent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(total_amount * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'reservation_id': reservation.reservation_id,
                    'user_email': request.user.email
                }
            )
            
            return render(request, 'Restaurant_handling/payment.html', {
                'reservation': reservation,
                'total_amount': total_amount,
                'client_secret': intent.client_secret,
                'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
            })
            
        except Exception as e:
            messages.error(request, f"Payment error: {str(e)}")
            return redirect('restaurant_detail', business_id=reservation.business_id.business_id)
    
    return render(request, 'Restaurant_handling/payment.html', {
        'reservation': reservation,
        'total_amount': total_amount,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY
    })

def payment_success(request, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id, 
                                  user_id=request.user)
    
    # Update reservation status
    reservation.reservation_status = 'Confirmed'
    reservation.save()
    
    # Send confirmation email
    send_reservation_email(request.user, reservation)
    
    messages.success(request, 'Payment successful! Your reservation is confirmed.')
    return redirect('Restaurant_handling:restaurant_detail', business_id=reservation.business_id.business_id)

def payment_cancel(request, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id, 
                                  user_id=request.user)
    
    messages.warning(request, 'Payment was cancelled. Your reservation is still pending.')
    return redirect('Restaurant_handling:restaurant_detail', business_id=reservation.business_id.business_id)

# views.py
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse

@require_POST
def process_payment(request, reservation_id):
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
                reverse('Restaurant_handling:payment_success', args=[reservation_id])
            ),
            metadata={
                'reservation_id': reservation.reservation_id,
                'user_email': request.user.email
            }
        )
        
        if intent.status == 'succeeded':
            # Update reservation status
            reservation.reservation_status = 'Confirmed'
            reservation.save()
            
            # Send confirmation email
            send_reservation_email(request.user, reservation)
            
            return JsonResponse({
                'success': True,
                'redirect_url': reverse('Restaurant_handling:payment_success', args=[reservation_id])
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



@business_required
def upcoming_reservations(request, business_id):
    """
    View to display upcoming reservations for a business.
    """
    try:
        business = get_object_or_404(Business, business_id=business_id)
        
        # Get filter parameters
        date_filter = request.GET.get('date')
        status_filter = request.GET.get('status')
        
        # Get upcoming reservations
        current_datetime = timezone.now()
        reservations = Reservation.objects.filter(
            business_id=business,
            reservation_date__gte=current_datetime.date()
        ).filter(
            Q(reservation_date__gt=current_datetime.date()) |
            Q(
                reservation_date=current_datetime.date(),
                reservation_time__gt=current_datetime.time()
            )
        ).order_by('reservation_date', 'reservation_time')

        # Apply additional filters if provided
        if date_filter:
            try:
                filter_date = timezone.datetime.strptime(date_filter, '%Y-%m-%d').date()
                reservations = reservations.filter(reservation_date=filter_date)
            except ValueError:
                pass

        if status_filter:
            reservations = reservations.filter(reservation_status=status_filter)

        # Calculate counts
        total_upcoming = reservations.count()
        today_count = reservations.filter(
            reservation_date=current_datetime.date()
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
            'current_date': current_datetime.date(),
            'date_filter': date_filter,
            'status_filter': status_filter,
        }

        return render(
            request,
            'Restaurant_handling/upcoming_reservations.html',
            context
        )
        
    except Exception as e:
        messages.error(request, f"An error occurred while loading reservations: {str(e)}")
        return redirect('restaurant_home')
    
    
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
   
    return render(request, 'Restaurant_handling/reservation_details.html', context)

@business_required
def delete_reservation(request, business_id, reservation_id):
    reservation = get_object_or_404(Reservation, 
                                  reservation_id=reservation_id,
                                  business_id=business_id)
    messages.success(request, 'Reservation deleted successfully!')
    reservation.delete()
    return redirect('Restaurant_handling:upcoming_reservations', business_id=business_id)


@business_required
def manage_customers(request):
    business = Business.objects.get(business_owner=request.user)
    reservations = Reservation.objects.filter(business_id=business)
    return render(request, 'Restaurant_handling/manage_customers.html', {
        'reservations': reservations,
        'business': business
    })