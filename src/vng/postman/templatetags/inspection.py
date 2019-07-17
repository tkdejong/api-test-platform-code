import json

from django import template
from django.utils.translation import ugettext_lazy as _

register = template.Library()


def exception_as_string(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return ''
    return wrapper


@exception_as_string
@register.filter
def info(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    return obj['info']['schema']


@exception_as_string
@register.filter
def info_name(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    return obj['info']['name']


@exception_as_string
@register.filter
def info_calls(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    items = obj['item']

    # unpacking all eventual subfolders
    total_calls = []
    while True:

        calls = list(filter(lambda x: 'request' in x, items))
        folders = list(filter(lambda x: 'request' not in x, items))
        total_calls += calls
        if not folders:
            break
        items = []
        for f in folders:
            items += f['item']

    return total_calls


@exception_as_string
@register.filter
def build_url(value):
    return value['request']['url']['raw']


@exception_as_string
@register.filter
def build_method(value):
    return value['request']['method']


@exception_as_string
@register.filter
def build_script(value):
    test = list(filter(lambda x: x['listen'] == 'test', value['event']))
    if test:
        return '\n'.join(test[0]['script']['exec'])
    return _('No script available')
