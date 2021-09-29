from datetime import datetime
from django.contrib.auth.models import Group, User
from opac_schema.v2.models import ArticleFiles
from opac_schema.v1.models import (
    Journal as OpacJournal,
    Article as OpacArticle,
)

from core.models import GROUP_MANAGER, SCOPE_ALL_USERS, IngressPackage, Event


def _is_privileged_user(user):
    return GROUP_MANAGER in get_groups_names_from_user(user) or user.is_superuser() or user.is_staff()


def _get_objects_from_user_and_scope(user, scope, model_class):
    if scope == SCOPE_ALL_USERS and _is_privileged_user(user):
        return model_class.objects.all()
    else:
        return model_class.objects.filter(user=user)


def get_deposited_packages_from_user_and_scope(user, scope):
    return _get_objects_from_user_and_scope(user, scope, IngressPackage)


def get_events_from_user_and_scope(user, scope):
    return _get_objects_from_user_and_scope(user, scope, Event)


def get_user_from_username(username):
    return User.objects.get(username=username)


def get_users(include_superuser=False):
    return User.objects.filter(is_superuser=include_superuser)


def get_groups_names_from_user(user):
    return [g.name for g in user.groups.all()]


def get_groups_from_user(user):
    return Group.objects.filter(user=user)


def update_user_groups(user, user_groups):
    for group in get_groups():
        if group not in user_groups:
            user.groups.remove(group)

    for ug in user_groups:
        user.groups.add(ug)
        user.save()


def get_groups_from_groups_names(groups_names):
    return Group.objects.filter(name__in=groups_names)


def get_groups():
    return Group.objects.all()


def get_articles_files():
    return ArticleFiles.objects.all()


def get_article_files(pid):
    return ArticleFiles.objects.get(_id=pid)


def get_article_metadata(pid):
    return OpacArticle.objects.get(_id=pid)


def get_opac_journals():
    return OpacJournal.objects.all()


def add_event(user, event_name, annotation=None):
    event = Event()
    event.user = user
    event.name = event_name
    event.annotation = annotation
    event.status = Event.Status.INITIATED
    event.save()

    return event


def update_event(event, args):
    for k, v in args.items():
        setattr(event, k, v)
    event.datetime = datetime.utcnow()
    event.save()

    return event


def add_ingress_package(user, event_datetime, package_name):
    ip = IngressPackage()
    ip.user = user
    ip.datetime = event_datetime
    ip.package_name = package_name
    ip.status = IngressPackage.Status.RECEIVED
    ip.save()

    return ip
