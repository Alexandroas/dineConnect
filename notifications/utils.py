# notifications/utils.py
from .models import Notification

def create_notification(user, message):
    """
    Create a notification for a user
    """
    return Notification.objects.create(
        recipient=user,
        message=message
    )