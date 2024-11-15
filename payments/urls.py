from . import views
from django.urls import path
 
app_name = 'payments' 
 
urlpatterns =[
    path('payment/<int:reservation_id>/', views.payment_view, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('process-payment/<int:reservation_id>/',views.process_payment,name='process_payment'),
    path('payment-success/<int:reservation_id>/',views.payment_success,name='payment_success'),
    path('payment_history/',views.payment_history,name='payment_history'),
]