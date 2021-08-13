# SPF

## Dependencies
```shell
gettext
python 3.9
```

## Installing
_Developer environment_
```shell
# Create a virtual environment
virtualenv -p python3.9 .venv

# Access the virtual environment
source .venv/bin/activated

# Install dependencies
pip install -r requirements.txt

# Access the spf root directory
cd spf

# Make migrations related to the database (at this moment, we're using a simple database - sqlite)
python manage.py makemigrations

# Migrate database (this operation construct all the necessary database tables)
python manage.py migrate

# Create the superuser (take note of the credentials)
python manage.py createsuperuser

# Start the application
python manage.py runserver
```

_Translation_
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

## Populating database
```shell
# Add content to the main tables
python manage.py loaddata user &
python manage.py loaddata group &
python manage.py loaddata document_file &
python manage.py loaddata document &
python manage.py loaddata package &
python manage.py loaddata journal &
```

## Usage
After following the installing and running instructions, the application must be accessible through the address http://127.0.0.1:8000.


## Observations
Keep in mind that this is an initial version of our application. 
The idea, at this moment, is to provide a simple interface where users can register and login into the system.
