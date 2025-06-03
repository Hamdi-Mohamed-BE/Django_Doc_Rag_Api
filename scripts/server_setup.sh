#! /bin/sh
python ../app/manage.py migrate --noinput
python ../app/manage.py collectstatic --noinput --clear
python ../app/manage.py createsuperuser --noinput