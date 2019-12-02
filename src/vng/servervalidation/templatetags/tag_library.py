from django import template

from vng.postman.utils import get_call_result as _get_call_result

register = template.Library()


@register.filter
def to_int(value):
    return int(value)


@register.filter
def index(l, i):
    return l[int(i)]

@register.filter
def get_call_result(value):
    return _get_call_result(value)
