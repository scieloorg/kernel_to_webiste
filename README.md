# SPF

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

## Usage
After following the install and run instructions, the application must be accessible through the address http://127.0.0.1:8000.


## Observations
Keep in mind that this is an initial version of our application. 
The idea, at this moment, is to provide a simple interface where users can register and login into the system.
