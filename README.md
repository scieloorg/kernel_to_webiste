# SPF

## Dependencies
Be sure that you have the necessary operational system dependencies:
```shell
gettext
python 3.9
```


## Installation

_Create a virtual environment and install the application dependencies_
```shell
# Create a virtual environment
virtualenv -p python3.9 .venv

# Access the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Set the environment variables (see config.ini.template)
Set the necessary environment variables under a developer machine through the following command: `export $(cat config.ini.template | xargs) `

## Prepare and run the application
```shell
# Access the spf root directory
cd spf

# Make migrations related to the database (at this moment, we're using a simple database - sqlite)
python manage.py makemigrations

# Migrate database (this operation construct all the necessary database tables)
python manage.py migrate

# Create the superuser (take note of the credentials)
python manage.py createsuperuser
```

_Add example data to the application database_
```shell
# Add content to the application tables
python manage.py loaddata group
python manage.py loaddata user
```

_Run the application_
```shell
# Start the application
python manage.py runserver
```


## How to translate the interface content to other languages
```shell
# Access the core project directory
cd core

# Create the strings translated to Portuguese
django-admin makemessages -l pt

# Create the strings translated to Spanish
django-admin makemessages -l es

# Compile the translated strings
django-admin compilemessages
```


## Usage
After following the installing and running instructions, the application must be accessible through the address http://127.0.0.1:8000.


## Observations
Keep in mind that this is an initial version of our application. 
The idea, at this moment, is to provide a simple interface where users can register and login into the system.
