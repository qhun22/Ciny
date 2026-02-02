"""
Custom template filters for PhoneShop.
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def format_number(value):
    """
    Format number with dot separator (Vietnamese style).
    Usage: {{ value|format_number }}
    Example: 16792000 -> 16.792.000
    """
    try:
        return f"{int(value):,}".replace(',', '.')
    except (ValueError, TypeError):
        return value


@register.filter
def format_vnd(value):
    """
    Format price to đ currency with dot separator.
    Usage: {{ price|format_vnd }}
    Example: 16792000 -> 16.792.000đ
    """
    try:
        return f"{int(value):,}".replace(',', '.') + "đ"
    except (ValueError, TypeError):
        return f"{value}"


@register.filter
@stringfilter
def format_vnd_str(value):
    """
    Format string price to đ currency with dot separator.
    Usage: {{ "1000000"|format_vnd_str }}
    Example: 1000000 -> 1.000.000đ
    """
    try:
        return f"{int(value):,}".replace(',', '.') + "đ"
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
