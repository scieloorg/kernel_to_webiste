# SciELO Publishing Framework


## Installation under a Python virtual environment

_System dependencies_

Be sure that you have the necessary operational system dependencies:

```shell
gettext
python 3.9
```

_Create a virtual environment and install the application dependencies_

```shell
# Create a virtual environment
virtualenv -p python3.9 .venv

# Access the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install packages
pip install .
```

_Set the environment variables_

```shell
export $(cat dev.ini | xargs)
```

_Create a PostgreSQL database named "spf"_

```shell
# Through a Docker container with a PostgreSQL database
docker exec --user postgres -it scielo-postgres-1 psql -c 'create database spf;'

# Or through psql
psql --user postgres;
create database spf;
```

_Run the Message Broker RabbitMQ_
```shell
# See https://www.rabbitmq.com/download.html to obtain more information
docker run -d -p 5672:5672 rabbitmq
```

_Prepare and run the application_

```shell
# Make migrations related to the database
python spf/manage.py makemigrations

# Migrate database (this operation will create all the necessary tables)
python spf/manage.py migrate

# Create the superuser (take note of the credentials)
python spf/manage.py createsuperuser
```

_Add default groups to the application database_

```shell
# Add default groups to the application database
python spf/manage.py loaddata group
```

_Add example users to the application database (only in development environments)_

```shell
# Add example users to the application database
python spf/manage.py loaddata user
```

_Run the application_

```shell
# Start Celery
celery -A spf worker -l INFO

# Start the application
python spf/manage.py runserver
```

_How to translate the interface content to other languages_

```shell
# Access the core project directory
cd core

# Create the strings translated to Portuguese
python ../manage.py make_messages_no_fuzzy -l pt

# Create the strings translated to Spanish
python ../manage.py make_messages_no_fuzzy -l es

# Compile the translated strings
python ../manage.py compilemessages
```

## Installation under Docker

```shell
# Ensure you are in the project root directory. Executing `ls .` will list the following files/directories:
dev.env
docker-compose.yml
docker-entrypoint.sh
Dockerfile
LICENSE
prod.env
README.md
requirements.txt
setup.py
spf

# Build image
docker-compose -f docker-compose.yml build

# Create and start a container with the image built
docker-compose up

# Make sure PostgreSQL and MongoDB databases are in the same network as the spf application
```

## List of environmental variables

Variable | Example value | Description
---------|---------------|------------
MINIO_HOST | `172.17.0.2:9000` | MinIO host address
MINIO_ACCESS_KEY | `minioadmin` | MinIO username
MINIO_SECRET_KEY | `minioadmin` | MinIO password
MINIO_TIMEOUT | `10000` | MinIO connection timeout
MINIO_SECURE | `false` | MinIO SSL flag (`true` or `false`)
MINIO_SCIELO_COLLECTION | `spf_brazil` | MinIO collection name
MINIO_SPF_DIR | `packages` | MinIO storage main directory
PID_DATABASE_DSN | `postgresql+psycopg2://postgres:password@172.17.0.4:5432/pidmanager` | PID manager (PostgreSQL) string connection
DATABASE_CONNECT_URL | `mongodb`://172.17.0.3:27017/opac | OPAC/Kernel database (MongoDB) string connection
DJANGO_DEBUG | `1` | Django flag to see DEBUG messages)
DJANGO_SECRET_KEY | `my_django_secret_key` |
DJANGO_ALLOWED_HOSTS | `localhost;127.0.0.1;[::1]` |
POSTGRES_DB | `spf` | SciELO Publishing Framework database name
POSTGRES_USER | `postgres` | SciELO Publishing Framework database user
POSTGRES_PASSWORD | `password` | SciELO Publishing Framework database user password
POSTGRES_HOST | `172.17.0.4` | SciELO Publishing Framework database hostname
POSTGRES_PORT | `5432` | SciELO Publishing Framework database host port
DJANGO_MANAGE_MIGRATE | `1` | Django flag to run `managep.py migrate`
DJANGO_MANAGE_LOAD | `1` | Django flag to run `manage.py loaddata group`
DJANGO_ADMIN_TRANSLATE | `1` | Django flag to run `django-admin compile_messages`
CELERY_BROKER_URL | `pyamqp://172.17.0.5:5672` | RabbitMQ address
CELERY_RESULT_BACKEND | `django-db` | Celery flag to use Django Database for persisting messages
