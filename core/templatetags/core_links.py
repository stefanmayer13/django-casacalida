import re

from django import template
from django.core.urlresolvers import reverse, NoReverseMatch

register = template.Library()

@register.simple_tag(takes_context=True)
def active_link(context, link, class_name='active'):
    try:
        pattern = '^' + reverse(link) + '$'
    except NoReverseMatch:
        pattern = link
    path = context['request'].path
    if re.search(pattern, path):
        return class_name
    return ''
