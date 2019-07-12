import json

from django import template

register = template.Library()


@register.filter
def info(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    return obj['info']['schema']


@register.filter
def info_name(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    return obj['info']['name']


@register.filter
def info_calls(value):
    with open(value.path) as infile:
        obj = json.load(infile)
    return obj['item']


@register.filter
def build_url(value):
    return value['request']['url']['raw']


@register.filter
def build_method(value):
    return value['request']['method']
