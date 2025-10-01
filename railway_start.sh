#!/bin/bash
# Railway startup script for Django

echo "🚀 Starting Joggle Django App on Railway..."

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Create superuser if it doesn't exist (optional)
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. You can create one later.')
else:
    print('Superuser already exists.')
"

# Start the application
echo "🌟 Starting Gunicorn server..."
exec gunicorn joggle.wsgi --bind 0.0.0.0:$PORT --log-file -
