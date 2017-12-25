# API Docs

- /api/register/ - POST - register user
- /api/login/ - POST- login user
- /api/logout/ - GET - logout user
- /api/forgot_password/ - POST - forgot password user
- /api/set_password/ - POST - set password (login required)
- /api/create_team/ - POST - create team (login required)
- /api/invite/ - POST - invite user (login required)

# How to run the project locally
- pip install -r requirements.txt
- python manage.py migrate
- python manage.py runserver
- go to http://localhost:8000/api/register/


# link to live demo on Heroku
https://drfik.herokuapp.com/api/register/

