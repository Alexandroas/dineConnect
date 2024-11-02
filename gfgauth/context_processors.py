# gfgauth/context_processors.py

def user_context(request):
    context = {
        'is_business': False
    }
    
    if request.user.is_authenticated:
        # Check if user is in Business group
        context['is_business'] = request.user.groups.filter(name='Business').exists()
    
    return context