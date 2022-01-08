#!/bin/sh

python manage.py collectstatic --no-input

gunicorn ultima_tea.wsgi:application --bind 0.0.0.0:8000
