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
At this point, we install pip, apache, and mod_wsgi.
```shell
sudo apt update
sudo apt install python3-pip
sudo apt install apache2
sudo apt install libapache2-mod-wsgi-py3
```

Since it's always recommended to use a virtual environment when working with a python project, we go ahead and install
the virtualenv package using pip:

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
virtualenv FiveGuysPowerTestingEnv
source FiveGuysPowerTestingEnv/bin/activate
```
Within this virtual environment we will install django.
```shell
pip install django
```

### Modify settings.py

We now have to change the `settings.py` file to include our server's public ip address. In this case, it is the same as
our VM's hostname. Navigate to the line 
```python
ALLOWED_HOSTS = []
```
and change it to
```python
ALLOWED_HOSTS = ['vcm-00000.vm.duke.edu']
```

We also have to configure the static directory. This setting will be at the bottom of the file.

```python
...
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static/'
...
```

### Collect Static Files
Next, we migrate our database to SQLite

```shell
./manage.py makemigrations
./manage.py migrate
```