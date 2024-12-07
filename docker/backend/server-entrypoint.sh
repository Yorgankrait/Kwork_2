#!/bin/sh

until cd /app/backend
do
    echo "Waiting for server volume..."
done


#until python manage.py migrate
#do
#    echo "Waiting for db to be ready..."
#    sleep 2
#done


python manage.py collectstatic --noinput

# python manage.py createsuperuser --noinput

gunicorn backend.wsgi --bind 0.0.0.0:8000 --workers 1 --threads 2

# for debug
#python manage.py runserver 0.0.0.0:8000