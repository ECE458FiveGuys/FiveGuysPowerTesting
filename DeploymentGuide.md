# Five Guys Deployment Guide

## Prerequisites

* 2 Virtual Machines running Ubuntu 20.04.2 LTS

### Reserve Virtual Machine

You will need to reserve two virtual machines: one for the frontend and one for the backend.

Navigate to <https://vcm.duke.edu/reservations/new/vm?> and select `Ubuntu Server 20.04`. Click `Agree` at the bottom
left-hand corner of the screen. Note the hostname of your virtual machine. It should follow the format
`vcm-#####.vm.duke.edu`. The instructions will use the placeholder hostname `vcm-00000.vm.duke.edu`.

### Access Virtual Machine

After reserving our Ubuntu VM, we need to access it. We will do so using ssh. Here, `netid` is a placeholder.

```shell
ssh netid@vcm-00000.vm.duke.edu
```

## Backend
### Install required software & packages

At this point, we install pip and nginx

```shell
sudo apt update
sudo apt install python3-pip python3-dev nginx snapd
sudo apt update
```

Next, we install core and certbot using snap.

```shell
sudo snap install core 
sudo snap refresh core
sudo snap install --classic certbot
```

Finally, we create a symbolic link to allow us to use the `certbot` command.

```shell
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Since it's recommended to use a virtual environment when working with a python project, we go ahead and install the
virtualenv package using pip:

```shell
sudo pip3 install virtualenv
```

### Clone git repository & set up environment

Next, we clone the git repo in the home directory of our VM.

```shell
git clone https://github.com/ECE458FiveGuys/FiveGuysPowerTesting
```

We then navigate to the project folder and create a new virtual environment.

```shell
cd FiveGuysPowerTesting
python3 -m virtualenv env
source env/bin/activate
```

Within this virtual environment we will install all the requirements in requirements.txt.

```shell
pip install -r requirements/server.txt
```

### Modify settings.py

We now have to change the `settings.py` file to include our server's public ip address. In this case, it is the same as our VM's hostname. Navigate to the line

```python
ALLOWED_HOSTS = []
```

and change it to

```python
ALLOWED_HOSTS = ['vcm-00000.vm.duke.edu']
```

Also make sure to change `DEBUG = True` to `DEBUG = False` as we don't want all the debug information to be sent to anyone accessing our website as it is a security issue.

### Add Secrets

Add file `FiveGuysPowerTesting/FiveGuysPowerTesting/secret_settings.py.` This file should contain a single variable, `SECRET_KEY.` The value for this variable can generated using the following code:

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
    DEV_REDIRECT_URI = 'SECRET'
    PROD_REDIRECT_URI = 'SECRET'

```
### Database setup

Next, we migrate our database to SQLite. In this step, we will also create a superuser. As per the instructions, this initial user should have `username = admin`. 

```shell
python manage.py makemigrations database
python manage.py makemigrations user_portal
python manage.py migrate
python manage.py createsuperuser
```
 
Now, we can collect the static files for nginx to serve at a later step.

```shell
python manage.py collectstatic --noinput
```

### Test to make sure project can run locally

```shell
sudo ufw allow 8000
python manage.py runserver 0.0.0.0:8000
```

Now, navigate to <http://vcm-00000.vm.duke.edu:8000> and make sure you can see the default Django REST framework page.
If yes, then stop your server by typing `CTRL-C`.

### Serve project with Gunicorn

```shell
gunicorn --bind 0.0.0.0:8000 FiveGuysPowerTesting.wsgi
```

Navigate to <http://vcm-00000.vm.duke.edu:8000> once more and make sure you can see the default Django REST framework
page, only this time with no CSS. If yes, then stop your server by typing `CTRL-C`. We are done with the virtual
environment for now, so type

```shell
deactivate
```

to deactivate the python virtual environment.

### Setup Gunicorn service file

Create the service file from the command line:

```shell
sudo nano /etc/systemd/system/gunicorn.service
```

In this file, type the following information. Replace `netid` with your user account on the vm, which should be your netid.

```text
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=netid
Group=www-data
WorkingDirectory=/home/netid/FiveGuysPowerTesting
ExecStart=/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting/bin/gunicorn --access-logfile - --workers 3 --timeout 960 --bind unix:/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting.sock FiveGuysPowerTesting.wsgi:application

[Install]
WantedBy=multi-user.target
```

Next, we want to start `Gunicorn` as well as make sure it runs on startup.

```shell
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

At this point, we want to make sure gunicorn is serving our project.

```shell
sudo systemctl status gunicorn
```

You should see a message showing that the service is active as long as the `gunicorn.service` file was written
correctly. If that is not the case, debugging can start by checking out the logs. The command for doing so is:

```shell
sudo journalctl -u gunicorn
```

### Connect to nginx

First, we make add a new server block for nginx

```shell
sudo nano /etc/nginx/sites-available/FiveGuysPowerTesting
```

In this file, type the following information. Again, replace `netid` with your user account on the vm, which should be your netid.

```text
server {
    listen 80;
    server_name vcm-00000.vm.duke.edu;
    client_max_body_size 36M;
    fastcgi_read_timeout 960;
    proxy_read_timeout 960;
    proxy_send_timeout 960;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/netid/FiveGuysPowerTesting;
    }
    location /media/ {
        root /home/netid/FiveGuysPowerTesting;
        autoindex on;
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            #
            # Om nom nom cookies
            #
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
            #
            # Custom headers and headers various browsers *should* be OK with but aren't
            #
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
            #
            # Tell client that this pre-flight info is valid for 20 days
            #
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain charset=UTF-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        if ($request_method = 'GET') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Credentials' 'true';
            add_header 'Access-Control-Allow-Methods' 'GET, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type';
        }
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting.sock;
    }
}
```

Now, we can link the file and restart nginx to make sure nginx only serves our project.

```shell
sudo ln -s /etc/nginx/sites-available/FiveGuysPowerTesting /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

Finally, we close port 8000 and open the ports defined by the server block file, i.e. port 80.

```shell
sudo ufw delete allow 8000
sudo ufw allow 'Nginx Full'
```

### Add SSL Encryption

We will be adding encryption using certbot. Run certbot using

```shell
sudo certbot --nginx
```

It will prompt you several times:

1) ask you for an email, 
   
2) ask whether you've read the terms of service (type `Y` and press `Enter`), 
  
3) ask whether you want to share your email (type `N` and press `Enter`), and 
  
4) ask which address you would like to install a certificate for (type `1` and press `Enter`).

```shell
sudo certbot --nginx
```

Now, navigate to <https://vcm-00000.vm.duke.edu> and make sure your connection is encrypted.

At this point, we should be done deploying the backend!

## Frontend
### Access Virtual Machine

After reserving our second Ubuntu VM, we need to access it. We will do so using ssh. Here, `netid` is a placeholder.

```shell
ssh netid@vcm-00000.vm.duke.edu
```

### Install required software & packages

At this point, we install and nginx and snap.

```shell
sudo apt update
sudo apt upgrade
sudo apt install nginx npm nodejs snapd
sudo apt update
```

Next, we install core and certbot using snap.

```shell
sudo snap install core 
sudo snap refresh core
sudo snap install --classic certbot
```

Finally, we create a symbolic link to allow us to use the `certbot` command.

```shell
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

### Add environment variables for OAuth

Add variables to the `/etc/environment` file. Here, the `SECRET` values should be the same value as the corresponding variable in the enum in the backend server. The following two variables should be added to the end of the environment file.

```shell
REACT_APP_CLIENT_ID=SECRET
REACT_APP_REDIRECT_URI=SECRET
```

After adding the variables, exit this session and start another ssh session.

### Clone git repository & set up environment

Next, we clone the git repo in the home directory of our VM. Replace `hostname` with the hostname of your website.

```shell
git clone git@github.com:ECE458FiveGuys/FiveGuysFront.git hostname
```

### Build react project

Navigate to the project folder, install dependencies, and create a production build
```shell
cd hostname
npm install
npm run build
```

### Connect to nginx

First, we make add a new server block for nginx

```shell
sudo nano /etc/nginx/sites-available/hostname
```

In this file, type the following information. Replace `netid` with your user account on the vm, which should be your netid.


```text
server {
    server_name hostname;
    root /home/netid/hostname/build;
    index index.html index.htm;
    client_max_body_size 36M;
    fastcgi_read_timeout 960;
    proxy_read_timeout 960;
    proxy_send_timeout 960;

    location / {
        try_files $uri /index.html =404;
    }
}
```

Now, we can link the file and restart nginx.

```shell
sudo ln -s /etc/nginx/sites-available/myProject /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

### Add SSL Encryption

We will be adding encryption using certbot. Run certbot using

```shell
sudo certbot --nginx
```

It will prompt you several times:

1) ask you for an email, 
   
2) ask whether you've read the terms of service (type `Y` and press `Enter`), 
  
3) ask whether you want to share your email (type `N` and press `Enter`), and 
  
4) ask which address you would like to install a certificate for (type `1` and press `Enter`).

Now, navigate to <https://hostname> and make sure your connection is encrypted.

At this point, we should be done! Congratulations, you've deployed the project in a production environment.

