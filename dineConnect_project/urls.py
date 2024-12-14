"""
URL configuration for dineConnect_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from dineConnect_project import settings
from django.contrib.auth import views as auth_views
from gfgauth.forms import CustomPasswordResetForm
from django.urls import reverse_lazy
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gfgauth.urls')),
    path('main/', include('main.urls')),
    path('accounts/password/reset/',
    auth_views.PasswordResetView.as_view(
        template_name='gfgauth/password_reset_form.html',  # Make sure this matches your file structure
        email_template_name='gfgauth/password_reset_email.html',
        subject_template_name='gfgauth/password_reset_subject.txt',
        success_url='/accounts/password/reset/done/',
        form_class=CustomPasswordResetForm,
    ),
    name='password_reset'),
    path('accounts/password/reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='gfgauth/password_reset_done.html'
        ), 
        name='password_reset_done'),
    path('accounts/password/reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='gfgauth/password_reset_confirm.html'
        ), 
        name='password_reset_confirm'),
    path('accounts/password/reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='gfgauth/password_reset_complete.html'
        ), 
        name='password_reset_complete'),
    path('accounts/', include('allauth.urls')),
    path('notifications/', include('notifications.urls')),
    path('restaurant_handling/', include('Restaurant_handling.urls')),
    path('api/', include('notifications.urls')),
    path('payments/', include('payments.urls')),
    path('reservations/', include('reservations.urls')),
    path('graphs/', include('graphs.urls')),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)