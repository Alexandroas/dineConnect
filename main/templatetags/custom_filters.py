from django import template

register = template.Library()

@register.filter
def get_range(value):
    return range(value)


# templatetags/custom_filters.py
from django import template
register = template.Library()

@register.filter
def get_group_names(groups):
    return [group.name for group in groups]