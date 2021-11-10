# SciELO Publishing Framework

## Development

### Installation under a Python virtual environment

__System dependencies__

```shell
# Be sure that you have the necessary operational system dependencies
gettext
python3
```

__Create a virtual environment and install the application dependencies__

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

__Set the environment variables__

```shell
# Create a dotenv file (and add to it the necessary environment variables - see List of environment variables)
touch .env.dev

# Export its contents to the system enviroment
export $(cat .env.dev | xargs)
```

__Create a PostgreSQL database named "spf"__

```shell
# Through a Docker container with a PostgreSQL database
docker exec --user postgres -it scl_postgres_1 psql -c 'create database spf;'

# Or through psql
psql --user postgres;
create database spf;
```

__Run the Message Broker RabbitMQ__
```shell
# See https://www.rabbitmq.com/download.html to obtain more information
docker run -d -p 5672:5672 rabbitmq
```

__Prepare and run the application__

```shell
# Make migrations related to the database
python manage.py makemigrations

# Migrate database (this operation will create all the necessary tables)
python manage.py migrate

# Create the superuser (take note of the credentials)
python manage.py createsuperuser
```

__Add default groups to the application database__

```shell
# Add default groups to the application database
python manage.py loaddata group
```

__Add example users to the application database (only in development environments)__

```shell
# Add example users to the application database
python manage.py loaddata user
```

__Run the application__

```shell
# Start Celery
celery -A spf worker -l INFO

# Start the application
python manage.py runserver
```

__How to translate the interface content to other languages__

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


---

## Production

### Installation under Docker

```shell
# Be sure you are in the project root directory. Executing `ls .` will list the following files/directories
app
docker-compose.yml
LICENSE
nginx
README.md
```

__Start a nginx container and copy nginx.conf to /etc/nginx/conf.d__

__Start a postgres container and keep note of user credentials__

__Create a dotenv file (and add to it the necessary environment variables - see List of environment variables)__

```shell
touch .env.prod
```

__Build image and start the services__

```shell
docker-compose -f docker-compose.yml up -d --build
```

__Migrate data__

```shell
# Under host shell, run
docker-compose -f docker-compose.yml exec web python manage.py migrate --noinput

# Under docker shell, run
python manage.py migrate
```

__Collect static files__

```shell
# Under host shell, run
docker-compose -f docker-compose.yml exec web python manage.py collectstatic --no-input --clear

# Under docker shell, run
python manage.py collectstatic
```

__Load default groups__

```shell
# Under host shell, run
docker-compose -f docker-compose.yml exec web python manage.py loaddata group

# Under docker shell, run
python manage.py loaddata group
```

__Load example users (recommended only for development environment)__

```shell
# Under host shell, run
docker-compose -f docker-compose.yml exec web python manage.py loaddata user

# Under docker shell, run
python manage.py loaddata user
```

__Make sure PostgreSQL and MongoDB databases are in the same network as the spf application__


---

## List of environment variables

- CELERY_BROKER_URL: RabbitMQ address (`pyamqp://user:pass@host:port`)
- DATABASE_CONNECT_URL: OPAC/Kernel database (MongoDB) string connection (`mongodb://user:pass@host:port/opac`)
- DJANGO_ALLOWED_HOSTS: `localhost;127.0.0.1;[::1]`
- DJANGO_DEBUG: Django flag to see DEBUG messages (`1`)
- DJANGO_SECRET_KEY: Django secret key
- MINIO_ACCESS_KEY: MinIO username
- MINIO_HOST: MinIO host address (`host:port`)
- MINIO_SCIELO_COLLECTION: MinIO collection name
- MINIO_SECRET_KEY: MinIO password
- MINIO_SECURE: MinIO SSL flag (`true` or `false`)
- MINIO_SPF_DIR: MinIO storage main directory
- MINIO_TIMEOUT: MinIO connection timeout
- PID_DATABASE_DSN: PID manager (PostgreSQL) string connection (`postgresql+psycopg2://postgres:password@host:port/database`)
- POSTGRES_DB: SciELO Publishing Framework database name
- POSTGRES_HOST: SciELO Publishing Framework database hostname
- POSTGRES_PASSWORD: SciELO Publishing Framework database user password
- POSTGRES_PORT: SciELO Publishing Framework database host port
- POSTGRES_USER: SciELO Publishing Framework database user
