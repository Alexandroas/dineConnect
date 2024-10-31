# utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
def send_welcome_email(user):
    context = {
        'username': user.username,
        'first_name': user.first_name,
        'email': user.email,
    }
    
    html_message = render_to_string('main\email_welcome.html', context)
    
    send_mail(
        subject='Welcome to DineConnect!',
        message='',
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
def send_reservation_email(user, reservation):
    context = {
        'first_name': user.first_name,
        'user': user,
        'reservation': reservation,
        'business': reservation.business_id,  # Access the business through reservation
    }
    
    html_message = render_to_string('main\email_reservation.html', context)
    
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