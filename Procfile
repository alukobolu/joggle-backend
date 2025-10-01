release: python manage.py migrate
web: gunicorn joggle.wsgi --bind 0.0.0.0:$PORT --log-file - --access-logfile -
