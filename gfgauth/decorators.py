from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def regular_user_or_guest(view_func):
    """
    Decorator to allow access to a view only for regular users or anonymous users (guests).
    This decorator performs the following checks:
    1. If the user is not authenticated (guest), the view is allowed.
    2. If the user is authenticated and belongs to the 'Business' group, an error message is displayed and the user is redirected to the restaurant home page.
    3. If the user is authenticated and does not belong to the 'Business' group, the view is allowed.
    Args:
        view_func (function): The view function to be decorated.
    Returns:
        function: The wrapped view function with the added access control.
    """
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