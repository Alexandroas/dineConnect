from . import views
from django.urls import include, path

app_name = 'Restaurant_handling'

urlpatterns = [
    path('add_dish/', views.add_dish, name='add_dish'),
    path('edit_dish/<int:dish_id>/', views.edit_dish, name='edit_dish'),
    path('delete_dish/<int:dish_id>/', views.delete_dish, name='delete_dish'),
    path('restaurant_profile_settings/', views.restaurant_profile_settings, name='restaurant_profile_settings'),  # Corrected name
    path('restaurant_dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('restaurant_profile/', views.restaurant_profile, name='restaurant_profile'),
    path('restaurant_menu/', views.restaurant_menu, name='restaurant_menu'),
    path('restaurant/<int:business_id>/hours/', views.restaurant_detail, name='restaurant_detail'),
    path('restaurant_home/', views.restaurant_home, name='restaurant_home'),
    path('manage_customers/', views.manage_customers, name='manage_customers'),
    path('customer_details/<int:user_id>/', views.customer_details, name='customer_details'),
    path('settings/', views.settings, name='settings'),
]
