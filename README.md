battleground
============

A turn based tank game for Python bots


Running the project for development:

In a virtualenv do:

# install the dependencies
pip install -r requirements.txt

# create the database
python manage.py migrate

# create an admin user
python manage.py createsuperuser

# run the development server
python manage.py runserver

Then open the browser at http://127.0.0.1:8000/

# Running the Celery worker for running matches:
celery -A battleground worker -l info