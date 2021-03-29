# FiveGuysPowerTesting Backup Guide
## Prerequisites
* Root access to server currently hosting database
* Duke Virtual Machine running Ubuntu 20.04.2 LTS
## Assumptions
We will make the following assumptions in order to make it easier to read this document.
1. The VM with the database has hostname `hostname.colab.duke.edu`
2. The VM that will store the backups has hostname `backup.colab.duke.edu`  
3. Database was created following the instructions in the FiveGuysPowerTesting Deployment Guide (i.e. has a user `netid` with all privileges on database `fiveguyspowertesting`)
## Notes
* Every time you see the values `user`, `netid`, `hostname.colab.duke.edu`, and `backup.colab.duke.edu`, they should be replaced with more appropriate values.
## Steps
Ideally, we would create a new user, `pgsql_backup`, on the server hosting the database for security purposes. However, since we are using Duke VMs, it is difficult to add a new user to our Linux server. As such, we will be accessing the server as the user `netid`, where `netid` is the account of the user who owns the VM.
### Reserve Virtual Machine
You will need to reserve a new virtual machine to store the backups.

Navigate to <https://vcm.duke.edu/reservations/new/vm?> and select `Ubuntu Server 20.04`. Click `Agree` at the bottom
left-hand corner of the screen. Note the hostname of your virtual machine. It should follow the format
`vcm-#####.vm.duke.edu`. The instructions will assume you added an alias, `backup.colab.duke.edu`, for this virtual machine.
### Access Virtual Machine
After reserving our Ubuntu VM, we need to access it. We will do so using ssh. Here, `netid` is a placeholder.
```shell
$ ssh netid@backup.colab.duke.edu
```
### Create New User
We will create a new user in the virtual machine so that other admins are able to login to an account not connected to
any netid. To create a new user, execute the command
```shell
user@backup.colab.duke.edu $ sudo useradd -m pgsql_backup
```
Now, we need to create a password for this user. You can compute the sha512 hash using salt `xyz` of password `HardPassword` 
by executing the command
```shell
user@backup.colab.duke.edu $ openssl passwd -6 -salt xyz HardPassword
```
Next, open the file `/etc/shadow`. At the bottom, you should see the line
```text
pgsql_backup:*:18708:0:99999:7:::
```
Replace the `*` (or whatever is between the first `:` and second `:`) with the output of our previous command.

Finally, we want to change the default shell of the user `pgsql_backup` to bash. We can do so by opening up the file `/etc/passwd`. At
the bottom of the file, you should see the line
```text
pgsql_backup:x:1001:1003::/home/pgsql_backup:/bin/sh
```
Change `/bin/sh` to `/bin/bash`.

Now, we add `pgsql_backup` to do the list of sudoers by adding the line
```text
pgsql_backup ALL=(ALL) ALL
```
to the bottom of the sudoers file. This file can be accessed by executing the command
```shell
user@backup.colab.duke.edu $ sudo visudo
```
Now, we can exit our current session and start a new session as the user `pgsql_backup`.
```shell
user@backup.colab.duke.edu $ exit
$ ssh pgsql_backup@backup.colab.duke.edu
```
### Install Dependencies
We will install a tool called `rsnapshot`, which we will use for maintaining our staggered backups, and another tool called `mailutils`, which we will use to notify the system administrator of the status of the backups.
```shell
pgsql_backup@backup.colab.duke.edu $ sudo apt install rsnapshot
pgsql_backup@backup.colab.duke.edu $ sudo apt install mailutils
```
You will be prompted for some configurations for `postfix` when installing `mailutils`. For our purposes, the default settings are sufficient.
### Link Backup Server and Database Server
#### Create .ssh folder
```shell
pgsql_backup@backup.colab.duke.edu $ mkdir .ssh
```
#### Create ssh key
Create the ssh key that we will use to access the server with the PostgreSQL database. You can do so by executing the command
```shell
pgsql_backup@backup.colab.duke.edu $ ssh-keygen -t ed25519 -f /home/pgsql_backup/.ssh/backup -q -P ""
```
Note that the option `-P ""` creates a ssh key with no passphrase, which means that they key is stored as plaintext. It is recommended that you do not do this. Instead, provide a secure password.
#### Add key to authorized_keys file
Next, we will copy this public key to the server's `~/.ssh/authorized_keys` file using `ssh-copy-id`. You will be prompted for the user `netid`'s password.
```shell
pgsql_backup@backup.colab.duke.edu $ ssh-copy-id -i ~/.ssh/backup.pub netid@hostname.colab.duke.edu
```
### Create Backup Folder
```shell
pgsql_backup@backup.colab.duke.edu $ mkdir backup
```
### Create Backup Scripts
We will create two scripts that we will use to backup our database. First, we will write a script to retrieve a dump of the database from the database server. We will call this script `backup_pgsql.sh`
```shell
pgsql_backup@backup.colab.duke.edu $ sudo nano /usr/local/bin/backup_pgsql.sh
```
Copy the following into the script:
```bash
#!/bin/bash

/usr/bin/ssh -i /home/pgsql_backup/.ssh/backup netid@hostname.colab.duke.edu "/usr/bin/pg_dump -Fc fiveguyspowertesting" > fiveguyspowertesting.dump
/usr/bin/chmod 644 fiveguyspowertesting.dump
```
Next, we will create a wrapper for `rsnapshot` (more on this tool in the next section) that will send an email based on whether the script was executed successfully or failed:
```shell
pgsql_backup@backup.colab.duke.edu $ sudo nano /usr/local/bin/rsnapshot_wrapper.sh
```
Copy the following into the script:
```bash
#!/bin/bash

interval=$1

OUTPUT=`rsnapshot ${interval}`
if [ $? -ne 0 ]
then
   echo -e "There was a problem with the scheduled backup. Below is the output of backup_pgsql.sh, if it ran.\n\n${OUTPUT}" | mail -s "${interval^} Backup Failure" admin@example.com
else
   echo -e "The scheduled backup succeeded. Below is the output of backup_pgsql.sh.\n\n${OUTPUT}" | mail -s "${interval^} Backup Success" admin@example.com
fi
```
Be sure to change `admin@example.com` to the email address of the system administrator.

Finally, change the file permissions so that they can be executed:
```shell
pgsql_backup@backup.colab.duke.edu $ sudo chmod 755 /usr/local/bin/backup_pgsql.sh  
pgsql_backup@backup.colab.duke.edu $ sudo chmod 755 /usr/local/bin/rsnapshot_wrapper.sh
```
### Use rsnapshot and crontab
First, we will change `/etc/rsnapshot.conf` to use this script to backup our database with a staggered retention (7 daily backups, 4 weekly backups, 12
monthly backups). Open the file with the following command
```shell
pgsql_backup@backup.colab.duke.edu $ sudo nano /etc/rsnapshot.conf
```
and copy the file shown here, replacing `netid` and `hostname` as needed. Make sure the separate commands using tabs, not spaces, or else the file will throw errors.
```text
#################################################
# rsnapshot.conf - rsnapshot configuration file #
#################################################
config_version  1.2

###########################
# SNAPSHOT ROOT DIRECTORY #
###########################

snapshot_root   /home/pgsql_backup/backup/

#################################
# EXTERNAL PROGRAM DEPENDENCIES #
#################################

cmd_cp          /bin/cp
cmd_rm          /bin/rm
cmd_rsync       /usr/bin/rsync
cmd_ssh         /usr/bin/ssh
cmd_logger      /usr/bin/logger

#########################################
#     BACKUP LEVELS / INTERVALS         #
#########################################

retain  daily   7
retain  weekly  4
retain  monthly 12

############################################
#              GLOBAL OPTIONS              #
############################################

verbose         5
loglevel        5
lockfile        /var/run/rsnapshot.pid

###############################
### BACKUP POINTS / SCRIPTS ###
###############################

backup_script   /usr/local/bin/backup_pgsql.sh  hostname.colab.duke.edu
```
Next, we will create the cron job by creating a cron table. Do so by modifying the table that was set up by rsnapshot with the following command:
```shell
pgsql_backup@backup.colab.duke.edu $ sudo nano /etc/cron.d/rsnapshot
```
Paste the following into the file:
```text
#################################################
#          crontab configuration file           #
#################################################
30 3    * * *   root    /usr/local/bin/rsnapshot_wrapper.sh daily
15 3    * * 1   root    /usr/local/bin/rsnapshot_wrapper.sh weekly
0  3    1 * *   root    /usr/local/bin/rsnapshot_wrapper.sh monthly
```
### Restore Database
To restore the database called `fiveguyspowertesting` with the file `backup.dump`, we can use the following commands:
```shell
pgsql_backup@backup.colab.duke.edu $ scp -i /home/pgsql_backup/.ssh/backup /path/to/file netid@hostname:/home/netid/
pgsql_backup@backup.colab.duke.edu $ ssh -i /home/pgsql_backup/.ssh/backup netid@hostname "sudo -u postgres dropdb fiveguyspowertesting"
pgsql_backup@backup.colab.duke.edu $ ssh -i /home/pgsql_backup/.ssh/backup netid@hostname "sudo -u postgres pg_restore -C -d postgres fiveguyspowertesting.dump"
```
### Test for Validity
The test for validity is similar to how we restore database, instead we target a developer server and not a production server.

First, we make a backup of the current state of the dev server and then we follow the instructions for restoring a database. Finally,
we can navigate to the url where the dev server is hosted and see if the restore was successful and the data is valid. Below is the code
that we would execute:
```shell
pgsql_backup@backup.colab.duke.edu $ ssh -i /home/pgsql_backup/.ssh/backup netid@devhost "sudo -u postgres pg_dump -Fc fiveguyspowertesting > test.dump"
pgsql_backup@backup.colab.duke.edu $ scp -i /home/pgsql_backup/.ssh/backup /path/to/file netid@hostname:/home/netid/
pgsql_backup@backup.colab.duke.edu $ ssh -i /home/pgsql_backup/.ssh/backup netid@devhost "sudo -u postgres dropdb fiveguyspowertesting"
pgsql_backup@backup.colab.duke.edu $ ssh -i /home/pgsql_backup/.ssh/backup netid@devhost "sudo -u postgres pg_restore -C -d postgres fiveguyspowertesting.dump"
```