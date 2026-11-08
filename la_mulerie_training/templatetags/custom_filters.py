from django import template

register = template.Library()

@register.filter
def percent_of(part, total):
    """Calculate percentage of part from total"""
    if total == 0:
        return 0
    try:
        return round((float(part) / float(total)) * 100, 1)
    except (ValueError, ZeroDivisionError):
        return 0
