#!/bin/sh

if [ "$DJANGO_MANAGE_MIGRATE" = "1" ]; then
    echo "making migrations ..."
    python spf/manage.py makemigrations
    echo "migrating data ..."
    python spf/manage.py migrate --noinput
fi

if [ "$DJANGO_CREATE_SUPERUSER" = "1" ]; then
    echo "creating superuser ..."
    python spf/manage.py createsuperuser \
    --noinput \
    --username $DJANGO_SUPERUSER_USERNAME \
    --email $DJANGO_SUPERUSER_EMAIL
fi

if [ "$DJANGO_MANAGE_LOAD_GROUP" = "1" ]; then
    echo "loading groups ..."
    python spf/manage.py loaddata group
fi

if [ "$DJANGO_MANAGE_LOAD_USER" = "1" ]; then
    echo "loading users ..."
    python spf/manage.py loaddata user
fi

if [ "$DJANGO_ADMIN_TRANSLATE" = "1" ]; then
    echo "translanting messages ..."
    django-admin compilemessages
fi

if [ "$DJANGO_COLLECTSTATIC" = "1" ]; then
    echo "collecting static files ..."
    python spf/manage.py collectstatic --noinput
fi

exec "$@"
