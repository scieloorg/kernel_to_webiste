FROM python:3.9.6-alpine

LABEL MAINTAINER scielo-dev@googlegroups.com
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk --update add --no-cache \
    git \
    gcc \
    build-base \
    libxml2-dev \
    libxslt-dev \
    py3-lxml \
    postgresql-dev \
    libffi-dev \
    gettext-dev

COPY . /app
WORKDIR /app

RUN pip install -U pip && \
    pip install -r /app/requirements.txt

RUN chmod +x /app/docker-entrypoint.sh
RUN chmod +x /app/docker-start-worker.sh

RUN chown -R nobody:nobody /app
USER nobody

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
