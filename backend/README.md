# celery command:

- celery -A backend worker --loglevel=INFO --pool=solo

- redis-cli -p 6379
- celery -A backend beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


# docker command:

- docker build -t backend .
- docker-compose -f backend/docker-compose.yml up --build -d (run from outside backend folder)

- docker build -t react-app:dev .

- docker-compose restart

- docker run -p 3000:3000 frontend

- docker-compose up
