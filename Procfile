web: gunicorn --workers=1 --threads=2 --worker-class=gthread --worker-connections=100 --max-requests=1000 --max-requests-jitter=100 --timeout=30 --keep-alive=2 --bind=0.0.0.0:$PORT wsgi:application
