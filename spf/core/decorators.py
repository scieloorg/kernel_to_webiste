from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _


def unauthenticated_user(view):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return view(request, *args, **kwargs)

    return wrapper


def allowed_users(allowed_groups=[]):
    def decorator(view):
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view(request, *args, **kwargs)
            elif request.user.groups.exists():
                for gn in [g.name for g in request.user.groups.all()]:
                    if gn in allowed_groups:
                        return view(request, *args, **kwargs)
                messages.warning(request,
                                 _('You do not have permission to access the requested page %s' % request.path),
                                 extra_tags='alert alert-warning')
                return redirect('index')
            messages.warning(request,
                             _('You do not have permission to access the requested page %s' % request.path),
                             extra_tags='alert alert-warning')
            return redirect('index')
        return wrapper
    return decorator
