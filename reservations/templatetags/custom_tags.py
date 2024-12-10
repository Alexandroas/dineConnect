from django import template
from django.contrib.auth import get_user_model

register = template.Library()

@register.filter
def has_user_allergens(dish, user):
    User = get_user_model()
    if isinstance(user, User):
        user_preferences = user.dietery_preference.all()
        dish_allergens = dish.allergens.all()
        return any(allergen in dish_allergens for allergen in user_preferences)
    return False