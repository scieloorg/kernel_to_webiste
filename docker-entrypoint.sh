#!/bin/sh

if [ "$DJANGO_MANAGE_MIGRATE" = "1" ]; then
    echo "migrating data ..."
    python spf/manage.py migrate --noinput
fi

if [ "$DJANGO_MANAGE_LOAD" = "1" ]; then
    echo "loading groups ..."
    python spf/manage.py loaddata group
fi

if [ "$DJANGO_ADMIN_TRANSLATE" = "1" ]; then
    echo "translanting messages ..."
    django-admin compilemessages
fi

exec "$@"
