FROM python:3.14-slim-bookworm
LABEL maintainer="amorallex@gmail.com"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user
USER django-user
COPY . /code/
