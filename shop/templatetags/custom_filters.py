"""
Custom template filters for PhoneShop.
"""

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter
def format_vnd(value):
    """
    Format price to VND currency.
    Usage: {{ price|format_vnd }}
    """
    try:
        return f"{int(value):,} VND"
    except (ValueError, TypeError):
        return f"{value}"


@register.filter
@stringfilter
def format_vnd_str(value):
    """
    Format string price to VND currency.
    Usage: {{ "1000000"|format_vnd_str }}
    """
    try:
        return f"{int(value):,} VND"
    except (ValueError, TypeError):
        return f"{value}"
