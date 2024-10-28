from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.custom_login, name='login'), 
    path('profile/<username>/', views.profile, name='profile'),  
    path('password_change/', views.password_change, name='password_change'),
    path('register_business/', views.register_business, name='register_business'),  
]