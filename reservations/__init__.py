from django import template

register = template.Library()

# Import and register your custom template tag
from .templatetags.custom_tags import has_user_allergens
register.filter('has_user_allergens', has_user_allergens)