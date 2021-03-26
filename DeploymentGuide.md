# Five Guys Power Testing Deployment Guide
## Prerequisites
* Virtual Machine running Ubuntu 20.04.2 LTS
### Reserve Virtual Machine
You will need to reserve two virtual machines: one for the frontend and one for the backend.

Navigate to <https://vcm.duke.edu/reservations/new/vm?> and select `Ubuntu Server 20.04`. Click `Agree` at the bottom
left-hand corner of the screen. Note the hostname of your virtual machine. It should follow the format
`vcm-#####.vm.duke.edu`. The instructions will use the placeholder hostname `vcm-00000.vm.duke.edu`.
### Access Virtual Machine
After reserving our Ubuntu VM, we need to access it. We will do so using ssh. Here, `netid` is a placeholder.
```shell
$ ssh netid@vcm-00000.vm.duke.edu
```
## Setup
### Install required software & packages
At this point, we install the dependencies we need for the front-end, back-end, and to deploy the both of them.
```bash
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install python3-pip python3-dev libpq-dev postgresql postgresql-contrib  # backend; database
$ sudo apt install npm nodejs                                                       # frontend
$ sudo apt install nginx snapd                                                      # server
```
Next, we install core and certbot using snap.
```shell
$ sudo snap install core 
$ sudo snap install --classic certbot
```
We also create a symbolic link to allow us to use the `certbot` command.
```shell
$ sudo ln -s /snap/bin/certbot /usr/bin/certbot
```
Since it's recommended to use a virtual environment when working with a python project, we go ahead and install the
virtualenv package using pip:
```shell
$ sudo pip3 install virtualenv
```
### Add environment variables for OAuth
Add variables to the `/etc/environment` file. Here, the `SECRET` values should be the same value as the corresponding variable in the enum in the backend server. The following two variables should be added to the bottom of the environment file.
```text
REACT_APP_CLIENT_ID=SECRET
REACT_APP_REDIRECT_URI=SECRET
```
After adding the variables, exit this session and start another ssh session. You can exit the session with the `exit` command:
```shell
$ exit
```
Start a new ssh session the same way we started it the first time:
```shell
$ ssh netid@vcm-00000.vm.duke.edu
```
### Clone front-end git repository
Next, we clone the git repo in the home directory of our VM. Replace `hostname` with the hostname of your website.
```shell
$ git clone git@github.com:ECE458FiveGuys/FiveGuysFront.git hostname
```
### Build react project

Navigate to the project folder, install dependencies, and create a production build

```shell
$ cd hostname
$ npm install
$ npm run build
$ cd ..
```

### Create PostgreSQL Database

When Postgres was installed, a new system user, `postgres` was added. We use this user to perform administrative tasks on the Postgres database.

```shell
$ sudo -u postgres psql
```

Now, we are in a postgres prompt. We seek to create a user and database for our project. We will set all the requesite permissions and then exit the prompt by executing the command  `\q`.

```console
postgres=# CREATE DATABASE fiveguyspowertesting;
postgres=# CREATE USER netid WITH PASSWORD 'HardPassword';
postgres=# ALTER USER netid CREATEDB;
postgres=# ALTER ROLE netid SET client_encoding TO 'utf8';
postgres=# ALTER ROLE netid SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE netid SET timezone TO 'UTC';
postgres=# GRANT ALL PRIVILEGES ON DATABASE fiveguyspowertesting TO netid;
postgres=# \q
```

### Clone back-end git repository & set up environment

Next, we clone the git repo in the home directory of our VM.

```shell
$ git clone git@github.com:ECE458FiveGuys/FiveGuysPowerTesting.git
```

We then navigate to the project folder and create a new virtual environment. We activate it with the `source` command.

```shell
$ cd FiveGuysPowerTesting
$ python3 -m virtualenv env
$ source env/bin/activate
```

Within this virtual environment we will install all the requirements in the file requirements/server.txt.

```shell
(env) $ pip install -r requirements/server.txt
```
### Add Secrets
Add file `FiveGuysPowerTesting/FiveGuysPowerTesting/secret_settings.py.` This file should contain all the variables that change based on whether the build is for production or development. In the example file below, you should be sure to change `hostname`, `netid`, and `HardPassword` to more appropriate values. Furthermore,
```python
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = '' # WE WILL GENERATE THIS VALUE

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['hostname', 'localhost']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'fiveguyspowertesting',
        'USER': 'netid',
        'PASSWORD': 'HardPassword',
        'HOST': 'localhost',
        'PORT': '',
    }
}
```
You would generate the value for `SECRET_KEY` by executing the following python code:
```python
import secrets

length = 50
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'

secret_key = ''.join(secrets.choice(chars) for i in range(length))

print(secret_key)
```
Next, add file `FiveGuysPowerTesting/user_portal/secrets.py` This file should contain an Enum class with four fields. Replace `'SECRET'` with value provided by Duke's OAuth group.
```python
from enum import Enum

class OAuthEnum(Enum):
    CLIENT_ID = 'SECRET'
    CLIENT_SECRET = 'SECRET'
    LOCAL_REDIRECT_URI = 'SECRET'
    DEV_REDIRECT_URI = 'SECRET'
    PROD_REDIRECT_URI = 'SECRET'

```
### Setup database tables
Next, we migrate our database to SQLite. In this step, we will also create a superuser. As per the instructions, this initial user should have `username = admin`.
```shell
(env) $ python manage.py makemigrations database
(env) $ python manage.py makemigrations user_portal
(env) $ python manage.py migrate
(env) $ python manage.py create_groups
(env) $ python manage.py createsuperuser --username admin --email admin@localhost
```

Now, we can collect the static files for nginx to serve at a later step.

```shell
(env) $ python manage.py collectstatic --noinput
```

### Test to make sure project can run locally

```shell
(env) $ sudo ufw allow 8000
(env) $ python manage.py runserver 0.0.0.0:8000
```

Now, navigate to <http://vcm-00000.vm.duke.edu:8000> and make sure you can see the default Django REST framework page.
If yes, then stop your server by typing `CTRL-C`.

### Serve project with Gunicorn

```shell
(env) $ gunicorn --bind 0.0.0.0:8000 FiveGuysPowerTesting.wsgi
```

Navigate to <http://vcm-00000.vm.duke.edu:8000> once more and make sure you can see the default Django REST framework
page, only this time with no CSS. If yes, then stop your server by typing `CTRL-C`. We are done with the virtual
environment for now, so type

```shell
(env) $ deactivate
```

to deactivate the python virtual environment.

### Setup Gunicorn service file

Create the service file from the command line:

```shell
$ sudo nano /etc/systemd/system/gunicorn.service
```

In this file, type the following information. Replace `netid` with your user account on the vm, which should be your netid.

```text
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=netid
EnvironmentFile=/etc/environment
Group=www-data
WorkingDirectory=/home/netid/FiveGuysPowerTesting
ExecStart=/home/netid/FiveGuysPowerTesting/env/bin/gunicorn --access-logfile - --workers 3 --timeout 960 --bind unix:/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting.sock FiveGuysPowerTesting.wsgi:application

[Install]
WantedBy=multi-user.target
```

Next, we want to start `Gunicorn` as well as make sure it runs on startup.

```shell
$ sudo systemctl start gunicorn
$ sudo systemctl enable gunicorn
```

At this point, we want to make sure gunicorn is serving our project.

```shell
$ sudo systemctl status gunicorn
```

You should see a message showing that the service is active as long as the `gunicorn.service` file was written
correctly. If that is not the case, debugging can start by checking out the logs. The command for doing so is:

```shell
$ sudo journalctl -u gunicorn
```

### Connect to nginx

First, we make add a new server block for nginx

```shell
$ sudo nano /etc/nginx/sites-available/hostname
```

In this file, type the following information. Again, replace `netid` with your user account on the vm, which should be your netid.

```nginx
server {
    server_name vcm-00000.vm.duke.edu;
    root /home/netid/hostname/build;
    index index.html index.htm;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }

    location /static/rest_framework/ {
        root /home/netid/FiveGuysPowerTesting; 
    }
    
    location /media/ {
        root /home/netid/FiveGuysPowerTesting;
        autoindex on;
    }
    
    location /api/ {
        include proxy_params;
        proxy_pass http://unix:/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting.sock;
    }

    location / {
        try_files $uri /index.html =404;
    }
}
```

Now, we can link the file and restart nginx to make sure nginx only serves our project.

```shell
$ sudo ln -s /etc/nginx/sites-available/hostname /etc/nginx/sites-enabled
$ sudo systemctl restart nginx
```

Finally, we close port 8000 and open the ports defined by the server block file, i.e. port 80.

```shell
$ sudo ufw delete allow 8000
$ sudo ufw allow 'Nginx Full'
```

### Add SSL Encryption

We will be adding encryption using certbot. Run certbot using

```shell
$ sudo certbot --nginx
```

It will prompt you several times to:



1) ask you for an email, 

2) ask whether you've read the terms of service (type `Y` and press `Enter`), 

3) ask whether you want to share your email (type `N` and press `Enter`), and 

4) ask which address you would like to install a certificate for (type `1` and press `Enter`).



Now, navigate to <https://vcm-00000.vm.duke.edu> and make sure your connection is encrypted.

Congratulations! You've succesfully deployed your project!
