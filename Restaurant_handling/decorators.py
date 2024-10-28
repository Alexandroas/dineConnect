from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.decorators import login_required
from gfgauth.models import Business  # Adjust import path as needed

def business_required(function=None, redirect_url='login'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # First check if user is authenticated
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check if user has an associated business
            try:
                business = Business.objects.get(business_owner=request.user)
                request.user.business = business  # Attach business to user object for convenience
                return view_func(request, *args, **kwargs)
            except Business.DoesNotExist:
                raise PermissionDenied("You must be a business owner to access this page.")
            
        return _wrapped_view
    
    if function:
        return decorator(function)
    return decorator