from datetime import datetime
from django.contrib.auth.models import Group, User
from opac_schema.v2.models import ArticleFiles
from opac_schema.v1.models import Journal as OPACJournal

from core.models import GROUP_MANAGER, SCOPE_ALL_USERS, IngressPackage, Event


def _is_privileged_user(user):
    return GROUP_MANAGER in get_groups_names_from_user(user) or user.is_superuser() or user.is_staff()


def _get_objects_from_user_and_scope(user, scope, model_class):
    if scope == SCOPE_ALL_USERS and _is_privileged_user(user):
        return model_class.objects.all()
    else:
        return model_class.objects.filter(user=user)


