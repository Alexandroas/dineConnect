def restaurant_context(request):
    business = None
    if hasattr(request.user, 'business'):
        business = request.user.business
    return {
        'business': business
    }