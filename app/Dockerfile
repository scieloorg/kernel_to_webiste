FROM python:3.9.6-alpine

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1

ENV PYTHONUNBUFFERED 1

RUN apk update \
    && apk add postgresql-dev \
    gcc \
    git \
    build-base \
    py3-lxml \
    python3-dev \
    musl-dev \
    libxml2-dev \
    libxslt-dev \
    libffi-dev \
    gettext-dev

RUN pip install --upgrade pip

COPY ./requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p /home/app

RUN addgroup -S app && adduser -S app -G app

ENV HOME=/home/app

ENV APP_HOME=/home/app/web

RUN mkdir ${APP_HOME}

RUN mkdir ${APP_HOME}/staticfiles

RUN mkdir ${APP_HOME}/mediafiles

WORKDIR ${APP_HOME}

COPY . ${APP_HOME}

RUN django-admin compilemessages

RUN chown -R app:app ${APP_HOME}

USER app
