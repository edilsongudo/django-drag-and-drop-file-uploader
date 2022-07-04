web: gunicorn fileUploader.wsgi --log-file -
worker: celery -A fileUploader worker --loglevel=info