from django import template
from django.contrib.auth.models import Group


register = template.Library()

@register.filter(name='has_group')
def has_group(user, group):
    group = Group.objects.get(name=group)
    return group in user.groups.all()
