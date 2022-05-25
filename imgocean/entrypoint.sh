#!/bin/sh
if [ "$DB_NAME" = "ocean" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata fixtures.json
python manage.py createdefaultadmin
python manage.py runserver 0.0.0.0:8000