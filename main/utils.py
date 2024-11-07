# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
# utils.py
def send_welcome_email(user, request=None, **kwargs):
    try:
        # Check if it's a social login
        if 'sociallogin' in kwargs:
            # Get user info from social account
            social_login = kwargs['sociallogin']
            email_context = {
                'username': user.username,
                'first_name': social_login.account.extra_data.get('given_name', user.username),
                'email': user.email,
            }
        context = {
            'username': user.username,
            'first_name': user.first_name,
            'email': user.email,
        }
        html_message = render_to_string('main/email_welcome.html', context)
       
        send_mail(
            subject='Welcome to DineConnect!',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
    
def send_reservation_email(user, reservation):
    context = {
        'user': user,
        'reservation': reservation,
        'business': reservation.business_id,
        'dishes' : reservation.dish_id.all(),
        'debug': True
    }
    print(f"Sending email for reservation {reservation.reservation_id}")
    print(f"Number of dishes: {reservation.dish_id.count()}")
    print(f"Dishes: {list(reservation.dish_id.all())}")
    html_message = render_to_string('main/email_reservation.html', context)
    
    try:
        send_mail(
            subject=f'Reservation Confirmation - {reservation.business_id.business_name}',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
    
    
    
    
def send_cancellation_email_business(user, reservation):
    context = {
        'user': reservation.user_id,
        
        'reservation': reservation,
        'business': reservation.business_id,
        'dishes' : reservation.dish_id.all(),
        'debug': True
    }
    print(f"Sending email for reservation {reservation.reservation_id}")
    print(f"Number of dishes: {reservation.dish_id.count()}")
    print(f"Dishes: {list(reservation.dish_id.all())}")
    html_message = render_to_string('main/cancellation_email_business.html', context)
    business_email = reservation.business_id.business_owner.email
    try:
        send_mail(
            subject=f'Reservation Cancellation - {reservation.business_id.business_name}',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[business_email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
    
def send_cancellation_email(user, reservation):
    context = {
        'user': user,
        'reservation': reservation,
        'business': reservation.business_id,
        'dishes' : reservation.dish_id.all(),
        'debug': True
    }
    print(f"Sending email for reservation {reservation.reservation_id}")
    print(f"Number of dishes: {reservation.dish_id.count()}")
    print(f"Dishes: {list(reservation.dish_id.all())}")
    html_message = render_to_string('main/cancellation_email.html', context)
    
    try:
        send_mail(
            subject=f'Reservation Cancellation - {reservation.business_id.business_name}',
            message='',
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False