from django import template
from django.contrib.auth.models import Group
from dateutil import parser


register = template.Library()


@register.filter(name='has_group')
def has_group(user, group):
    group = Group.objects.get(name=group)
    return group in user.groups.all()


@register.filter(name='to_datetime')
def to_datetime(text):
    if isinstance(text, str):
        try:
            return parser.parse(text)
        except:
            pass
    return text
