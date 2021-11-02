# SciELO Publishing Framework


## Installation under a Python virtual environment

_System dependencies_

Be sure that you have the necessary operational system dependencies:

```shell
gettext
python 3
```

_Create a virtual environment and install the application dependencies_

```shell
# Create a virtual environment
virtualenv -p python3 .venv

# Access the virtual environment
source .venv/bin/activate

# Access the folder app
cd app

# Install dependencies
pip install -r requirements.txt

# Install packages
pip install .
```

_Set the environment variables_

```shell
# Create a dotenv file (and add to it the necessary environment variables - see List of environmental variables)
touch .env.dev

# Export its contents to the system enviroment
export $(cat .env.dev | xargs)
```

_Create a PostgreSQL database named "spf"_

```shell
# Through a Docker container with a PostgreSQL database
docker exec --user postgres -it scl_postgres_1 psql -c 'create database spf;'

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
python manage.py makemigrations

# Migrate database (this operation will create all the necessary tables)
python manage.py migrate

# Create the superuser (take note of the credentials)
python manage.py createsuperuser
```

_Add default groups to the application database_

```shell
# Add default groups to the application database
python manage.py loaddata group
```

_Add example users to the application database (only in development environments)_

```shell
# Add example users to the application database
python manage.py loaddata user
```

_Run the application_

```shell
# Start Celery
celery -A spf worker -l INFO

# Start the application
python manage.py runserver
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
app
docker-compose.yml
LICENSE
nginx
README.md

# Create a dotenv file (and add to it the necessary environment variables - see List of environmental variables)
touch .env.prod

# Build image and start the services
docker-compose -f docker-compose.yml up -d --build

# Migrate data
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput

# Collect static files
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear

# Load default groups
docker-compose -f docker-compose.yml exec web python manage.py loaddata group

# Load example users
docker-compose -f docker-compose.yml exec web python manage.py loaddata user

# Make sure PostgreSQL and MongoDB databases are in the same network as the spf application
```

## List of environmental variables

Variable | Example value | Description
---------|---------------|------------
CELERY_BROKER_URL | `pyamqp://user:pass@host:port` | RabbitMQ address
DATABASE_CONNECT_URL | `mongodb://user:pass@host:port/opac` | OPAC/Kernel database (MongoDB) string connection
DJANGO_ALLOWED_HOSTS | `localhost;127.0.0.1;[::1]` |
DJANGO_DEBUG | `1` | Django flag to see DEBUG messages
DJANGO_SECRET_KEY | | Django secret key
MINIO_ACCESS_KEY | | MinIO username
MINIO_HOST | `host:port` | MinIO host address
MINIO_SCIELO_COLLECTION | | MinIO collection name
MINIO_SECRET_KEY | | MinIO password
MINIO_SECURE | | MinIO SSL flag (`true` or `false`)
MINIO_SPF_DIR | | MinIO storage main directory
MINIO_TIMEOUT | | MinIO connection timeout
PID_DATABASE_DSN | `postgresql+psycopg2://postgres:password@host:port/database` | PID manager (PostgreSQL) string connection
POSTGRES_DB | `database name` | SciELO Publishing Framework database name
POSTGRES_HOST | `localhost` | SciELO Publishing Framework database hostname
POSTGRES_PASSWORD | | SciELO Publishing Framework database user password
POSTGRES_PORT | | SciELO Publishing Framework database host port
POSTGRES_USER | | SciELO Publishing Framework database user
