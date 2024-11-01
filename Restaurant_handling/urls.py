from . import views
from django.urls import include, path

urlpatterns = [
    path('add_dish/', views.add_dish, name='add_dish'),
    path('edit_dish/<int:dish_id>/', views.edit_dish, name='edit_dish'),
    path('delete_dish/<int:dish_id>/', views.delete_dish, name='delete_dish'),
    path('restaurant_profile_settings/', views.restaurant_profile_settings, name='restaurant_profile_settings'),  # Corrected name
    path('restaurant_dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant_profile/', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant_menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/<int:business_id>/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurant_home/', views.restaurant_home, name='restaurant_home'),
    path('restaurant_reservation/<int:business_id>/', views.reservation, name='restaurant_reservation'),
    path('upcoming_reservations<int:business_id>/', views.upcoming_reservations, name='upcoming_reservations'),
    #path('business/<int:business_id>/reservations/', views.upcoming_reservations, name='upcoming_reservations'),    
   # path('business/<int:business_id>/', views.business_detail, name='business_detail'),
]
