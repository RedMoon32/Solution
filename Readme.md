## Solution  

### Instruction:
1) clone repo
2) run database:  `docker-compose up -d`
3) create venv: `virtualenv venv`
4) activate venv: `source venv/bin/activate`
5) install requirements: `pip install -r requirements.txt`
6) Go to working directory: `cd ws_parser`
7) Migrate database: `python manage.py migrate`
6) Load initial data (**preferable**): `python manage.py loaddata verif_parser/fixture.json`
 **or** parse data(may take too long): `python manage.py parse`
7) Create user to access web-site: `python manage.py createsuperuser`
8) Run server :`python manage.py runserver 8000`, and go to `http://127.0.0.1:8000/admin/` in browser to see data

### Code base
Main files are in verif_parser folder:` models.py, main_parser.py, tests.py, management/commands/parser.py`