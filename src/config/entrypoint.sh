# python manage.py runserver
APP_PORT=${PORT:-8000}
cd /app/
/apt/venv/bin/waitress home.wsgi:application --bind "0.0.0.0:${APP_PORT}"