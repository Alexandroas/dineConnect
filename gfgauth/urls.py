from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.custom_login, name='login'), 
    path('profile/<username>/', views.profile, name='profile'),  
    path('password_change/', views.password_change, name='password_change'),
    path('register/business/', 
         views.BusinessRegistrationWizard.as_view(views.FORMS), 
         name='register_business'), 
    # urls.py
    path('toggle-favorite/<int:business_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/', views.favorite_restaurants, name='favorite_restaurants'),
    path('view_reservation/<int:reservation_id>', views.view_reservation, name='view_reservation'),
    path('cancel_reservation/<int:reservation_id>', views.cancel_reservation, name='cancel_reservation'),
]