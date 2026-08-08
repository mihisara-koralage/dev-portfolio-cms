from django import template
from django.urls import resolve, reverse

register = template.Library()


@register.filter
def split(value, delimiter):
    """Split a string by delimiter."""
    return value.split(delimiter)


@register.simple_tag(takes_context=True)
def active_link(context, url_name, css_active='text-white', css_default='text-slate-400'):
    """
    Returns the active CSS class if the current URL matches url_name.

    Usage:
        {% active_link 'public:project-list' %}
        {% active_link 'public:blog-list' 'text-primary-400' 'text-slate-400' %}
    """
    request = context.get('request')
    if not request:
        return css_default
    try:
        current = resolve(request.path_info)
        target  = reverse(url_name)
        if request.path_info == target or request.path_info.startswith(target) and target != '/':
            return css_active
    except Exception:
        pass
    return css_default