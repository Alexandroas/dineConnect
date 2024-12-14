from django.http import HttpResponseRedirect, JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Notification
from django.utils.timezone import now
import json
import time
from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse
from django.contrib import messages



@csrf_exempt
def notification_stream(request):
    """
    View function to provide a server-sent events (SSE) stream of notifications for authenticated users.
    This view function streams notifications to the client in real-time using SSE. It checks for new notifications
    for the authenticated user every 5 seconds and sends them to the client if they haven't been sent before.
    Args:
        request (HttpRequest): The HTTP request object.
    Returns:
        StreamingHttpResponse: A streaming HTTP response with the notifications in SSE format.
    Notes:
        - The user must be authenticated to access this stream. If not, a 401 Unauthorized response is returned.
        - The notifications are filtered based on the recipient, creation time, and read status.
        - The response headers are set to prevent caching and disable buffering.
    """
    if not request.user.is_authenticated:
        return StreamingHttpResponse("Unauthorized", status=401)

    def event_stream():
        last_check = now()
        sent_notifications = set()  # Track sent notifications

        while True:
            try:
                notifications = Notification.objects.filter(
                    recipient=request.user,
                    created_at__gt=last_check,
                    is_read=False
                )
                
                for notification in notifications:
                    if notification.id not in sent_notifications:
                        data = {
                            'id': notification.id,
                            'message': notification.message,
                            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'is_read': notification.is_read
                        }
                        sent_notifications.add(notification.id)
                        yield f"data: {json.dumps(data)}\n\n"
                
                last_check = now()
                time.sleep(5)

            except Exception as e:
                print(f"Error in event stream: {e}")
                time.sleep(5)

    response = StreamingHttpResponse(
        event_stream(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    return response


@require_http_methods(["GET"])
def get_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
        
    notifications = Notification.objects.filter(recipient=request.user).values(
        'id', 
        'message', 
        'is_read', 
        'created_at'
    )
    notification_count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse(list(notifications), safe=False, headers={'X-Notification-Count': notification_count})

@require_http_methods(["POST"])
def mark_as_read(request, notification_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
        
    try:
        notification = Notification.objects.get(
            id=notification_id, 
            recipient=request.user
        )
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)

@require_http_methods(["POST"])
def mark_all_read(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
        
    Notification.objects.filter(recipient=request.user).update(is_read=True)
    messages.success(request, 'All notifications marked as read')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

@require_http_methods(["POST"])
def delete_all_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=403)
        
    Notification.objects.filter(recipient=request.user).delete()
    messages.success(request, 'All notifications deleted successfully')
    
    # Option 1: Redirect to previous page
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))