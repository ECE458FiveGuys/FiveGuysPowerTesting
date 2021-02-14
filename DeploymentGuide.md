# Five Guys Power Testing Deployment Guide

## Prerequisites

* Virtual Machine running Ubuntu 20.04.2 LTS
* Python3 (comes with Ubuntu 20.04.2 LTS)

### Reserve Virtual Machine

Navigate to <https://vcm.duke.edu/reservations/new/vm?> and select `Ubuntu Server 20.04`. Click `Agree` at the bottom
left-hand corner of the screen. Note the hostname of your virtual machine. It should follow the format
`vcm-#####.vm.duke.edu`. The instructions will use the placeholder hostname `vcm-00000.vm.duke.edu`.

### Access Virtual Machine

After reserving our Ubuntu VM, we need to access it. We will do so using ssh. Here, `netid` is a placeholder.

```shell
ssh netid@vcm-00000.vm.duke.edu
```

### Install required software & packages

At this point, we install pip and nginx

```shell
sudo apt update
sudo apt install python3-pip python3-dev nginx snapd
sudo apt update
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
### Database setup

Next, we migrate our database to SQLite

```shell
python manage.py makemigrations database
python manage.py makemigrations user_portal
python manage.py migrate
python manage.py createsupseruser
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
ExecStart=/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/netid/FiveGuysPowerTesting/FiveGuysPowerTesting.sock FiveGuysPowerTesting.wsgi:application

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

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/netid/FiveGuysPowerTesting;
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

We will be adding encryption using certbot. First, we install core and then certbot using snap, another package manager that we installed earlier.

```shell
sudo snap install core 
sudo snap refresh core
sudo snap install --classic certbot
```

Next, we create a symbolic link to allow us to use the `certbot` command.

```shell
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Finally, run certbot. It will prompt several times:

1) ask you for an email, 
   
2) ask whether you've read the terms of service (type `Y` and press `Enter`), 
  
3) ask whether you want to share your email (type `N` and press `Enter`), and 
  
4) ask which address you would like to install a certificate for (type `1` and press `Enter`).

```shell
sudo certbot --nginx
```

Now, navigate to <https://vcm-00000.vm.duke.edu> and make sure your connection is encrypted.

At this point, we should be done! Congratulations, you've deployed the project in a production environment.
