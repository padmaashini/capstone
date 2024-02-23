# CareQueue - Prioritizing Patient Requests

NLP + Request Management

## Setup (Windows)
- Clone the repo
- Setup your virtual environment by running `python -m venv venv`
- Activate your environment by running: 
    - On a bash shell: `source venv/Scripts/activate`
    - Windows Command Prompt: `venv\Scripts\activate.bat`
- Once you have activated your environment, install all dependencies, `pip install -r requirements.txt`
- To get superuser access to the application, run `python manage.py createsuperuser` but only after you have run `migrate` if you haven't done so already
    - Using the credentials set, you can now login to `http://127.0.0.1:8000/admin` 

## Getting your server up and running
- `python manage.py runserver` will start your server on `localhost:8000`
- `celery -A core beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler` will run the scheduler
- `celery -A core worker --loglevel=info` runs the Celery worker
- http://localhost:15672/#/

## Dev Tools
- To access the Django shell, run `python manage.py shell`
- Migrations
    - `python manage.py makemigrations`
    - `python manage.py migrate`

## Helpful Documentation
### Python/Django
- [Setting up your first project on Django](https://realpython.com/get-started-with-django-1/#what-youre-going-to-build)
- [Django and React](https://www.digitalocean.com/community/tutorials/build-a-to-do-application-using-django-and-react)
- [Django Rest Framework (DRF)](https://www.django-rest-framework.org/#example)
- [DRF Example](https://www.geeksforgeeks.org/django-rest-api-crud-with-drf/)
- [Relationships in Django](https://www.webforefront.com/django/setuprelationshipsdjangomodels.html#:~:text=Many%20to%20many%20relationships%20in,belong%20to%20many%20Store%20records.)
- [Super User Access](https://codinggear.blog/how-to-create-superuser-in-django/#:~:text=The%20easiest%20and%20most%20popular,email%2C%20and%20finally%20your%20password.)
### Other
- [Markdown Syntax Cheatsheet](https://www.markdownguide.org/cheat-sheet/)

## Languages, Frameworks, Tech Used
- Python with Django
- Celery
- RabbitMQ
