from . import views
from django.urls import path

app_name= "reservations"

urlpatterns = [
    path('restaurant_reservation/<int:business_id>/', views.make_reservation, name='restaurant_reservation'),
    path('upcoming_reservations/<int:business_id>/', views.upcoming_reservations, name='upcoming_reservations'),
    path('reservation_details/<int:business_id>/<int:reservation_id>/',views.reservation_details,name='reservation_details'),
    path('cancel_reservation/<int:business_id>/<int:reservation_id>/', views.cancel_reservation, name='cancel_reservation'),
    path('confirm_reservation/<int:business_id>/<int:reservation_id>/', views.confirm_reservation, name='confirm_reservation'),
    path('complete_reservation/<int:business_id>/<int:reservation_id>/', views.complete_reservation, name='complete_reservation'),
]
