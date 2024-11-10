from . import views
from django.urls import include, path

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/stream/', views.notification_stream, name='notification_stream'),
]

