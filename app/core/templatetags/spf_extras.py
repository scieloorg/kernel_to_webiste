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


@register.filter(name='to_css_event_status_style')
def to_css_event_status_style(event_status):
    if event_status == 'I':
        return 'bg-warning'
    elif event_status == 'C':
        return 'bg-success'
    elif event_status == 'F':
        return 'bg-danger'
    else:
        return 'bg-secondary'


@register.filter(name='to_css_ingress_package_status_style')
def to_css_ingress_package_status_style(ingress_package_status):
    if 'C' in ingress_package_status:
        return 'bg-success'
    elif 'Q' in ingress_package_status:
        return 'bg-secondary'
    elif 'I' in ingress_package_status:
        return 'bg-warning'
    elif 'F' in ingress_package_status:
        return 'bg-danger'

@register.filter(name='to_css_migration_status_style')
def to_css_migration_status_style(migration_status):
    if migration_status == 'pending_migration':
        return 'bg-secondary'
    return 'bg-danger'
