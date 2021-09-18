from django import template
from django.contrib.auth.models import Group
from django.utils.translation import gettext as _
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


@register.filter(name='to_short_group_name')
def to_short_group_name(group):
    if group == 'quality_analyst':
        return _('Q. Analyst')
    if group == 'operator_ingress':
        return _('Op. Ingress')
    if group == 'operator_migration':
        return _('Op. Migration')
    if group == 'manager':
        return _('Manager')
    return group.title()


