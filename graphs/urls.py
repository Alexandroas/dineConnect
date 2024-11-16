from django.urls import path
from .views import monthly_sales, analytics, montly_reservations, dish_popularity

app_name = 'graphs'

urlpatterns = [
    path('monthly_sales/<int:business_id>/', monthly_sales, name='monthly_sales'),
    path('analytics/<int:business_id>/', analytics, name='analytics'),
    path('monthly_reservations/<int:business_id>/', montly_reservations, name='monthly_reservations'),
    path('dish_popularity/<int:business_id>/', dish_popularity, name='dish_popularity'),
]

