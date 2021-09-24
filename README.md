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

_Prepare and run the application_

```shell
# Make migrations related to the database (at this moment, we're using a simple database - sqlite)
python spf/manage.py makemigrations

# Migrate database (this operation construct all the necessary database tables)
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
# Start the application
python spf/manage.py runserver
```

_How to translate the interface content to other languages_

```shell
# Access the core project directory
cd core

# Create the strings translated to Portuguese
django-admin makemessages_no_fuzzy -l pt

# Create the strings translated to Spanish
django-admin makemessages_no_fuzzy -l es

# Compile the translated strings
django-admin compilemessages
```


## Usage
After following the installing and running instructions, the application must be accessible through the address http://127.0.0.1:8000.


## Observations
Keep in mind that this is an initial version of our application. 
The idea, at this moment, is to provide a simple interface where users can authenticate, search and send packages.
