#!/bin/sh

# Check if its running in a container
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Create superuser from environment variables
echo "
import os
from django.contrib.auth import get_user_model

User = get_user_model()

# At the start, delete all users
User.objects.all().delete()

# Get info from environment variables
uname = os.environ.get('LOGIN_USERNAME', None)
passw = os.environ.get('LOGIN_PASSWORD', None)

# If not set, quit
if not (uname and passw):
    quit()

# If already exists, quit
if User.objects.filter(username=uname).exists():
    quit()

# Create the superuser
User.objects.create_superuser(uname, 'admin@admin.com', passw)
" | python3 manage.py shell


# python manage.py flush --no-input
python manage.py makemigrations
python manage.py migrate

exec "$@"