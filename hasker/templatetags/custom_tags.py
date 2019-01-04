# <app>/templatetags/custom_tags.py
from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def http_get_param_replace(context, **kwargs):
    """
    Return encoded URL parameters that are the same as the current
    request's parameters, only with the specified GET parameters added or changed.

    For example, if you're on the page 
    /questions/?tab=hot,

    then
    <a href="?{% get_param_replace page=2 %}"

    would expand to
    <a href="/questions/?page=2&tab=hot</a>

    Based on
    https://www.caktusgroup.com/blog/2018/10/18/filtering-and-pagination-django/
    """
    d = context['request'].GET.copy()
    for k, v in kwargs.items():
        d[k] = v
    return d.urlencode()


@register.simple_tag(takes_context=True)
def get_safe(context, value, default_value):
    return context.get(value, default_value)