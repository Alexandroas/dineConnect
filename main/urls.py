# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('testimonials/', views.add_edit_testimonial, name='testimonials'),   
]
