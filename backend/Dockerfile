FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Sets the working directory inside the container to /app.
WORKDIR /app

# Copies your Django backend project folder (on your host machine) into the container’s /app/ directory.
COPY . /app/

# install dependency
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN pip install gunicorn

# collect static file
RUN python manage.py collectstatic --no-input

# run django server with gunicorn
CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000"]


# docker-compose -f backend/docker-compose.yml up --build -d (run from outside backend folder)
