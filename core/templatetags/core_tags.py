# core/templatetags/core_tags.py
from django import template

register = template.Library()

@register.filter
def star_range(value):
    """Return range for star rating"""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def empty_star_range(value):
    try:
        return range(5 - int(value))
    except (ValueError, TypeError):
        return range(5)

@register.filter
def in_list(value, the_list):
    return value in the_list