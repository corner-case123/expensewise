from django import template

register = template.Library()


@register.filter
def percentage(value, total):
    """Calculate percentage: {{ value|percentage:total }}"""
    try:
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter
def abs_value(value):
    """Return absolute value: {{ value|abs_value }}"""
    try:
        return abs(float(value))
    except (ValueError, TypeError):
        return value
