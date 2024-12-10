from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def regular_user_or_guest(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Allow anonymous users (guests)
        if not request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        
        # Check if user is in Business group
        if request.user.groups.filter(name='Business').exists():
            messages.error(request, "This page is not accessible to business accounts.")
            return redirect('Restaurant_handling:restaurant_home')
            
        # Allow regular users
        return view_func(request, *args, **kwargs)
    return wrapper