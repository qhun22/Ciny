"""
Custom template filters for PhoneShop.
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def format_vnd(value):
    """
    Format price to đ currency.
    Usage: {{ price|format_vnd }}
    """
    try:
        return f"{int(value):,} đ"
    except (ValueError, TypeError):
        return f"{value}"


@register.filter
@stringfilter
def format_vnd_str(value):
    """
    Format string price to đ currency.
    Usage: {{ "1000000"|format_vnd_str }}
    """
    try:
        return f"{int(value):,} đ"
    except (ValueError, TypeError):
        return f"{value}"


@register.filter
def dictgetitem(dictionary, key):
    """
    Get value from dictionary by key.
    Usage: {{ my_dict|dictgetitem:my_key }}
    """
    try:
        return dictionary.get(key, 0)
    except (AttributeError, TypeError):
        return 0
