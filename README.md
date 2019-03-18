# SZR

[django-project-skeleton](https://github.com/Mischback/django-project-skeleton)  


## Installation For Linux
It's recommended to use virtual environment.  

Installation virtualenv for Python 3.6
```
sudo apt-get install python3-venv
```

create new virtual environment  
```
python3 -m venv ./tmp/venv
```  
active it  
```
. ./tmp/venv/bin/activate
```  

### Setup virtualenv  
It will install all necessary python libraries  
```
make setup/dev
```  

## Celery  
[How to use it](https://simpleisbetterthancomplex.com/tutorial/2017/08/20/how-to-use-celery-with-django.html "Article")  
[Supervisor](https://medium.com/@channeng/celery-scheduler-part-2-managing-celery-with-supervisor-2a0c6e7f7a6e "Article")  
[Setup for production](https://medium.com/@bencleary/django-scheduled-tasks-queues-part-2-fc1fb810b81d)
#### Installation  
Installing RabbitMQ on Ubuntu
```
sudo apt-get install -y erlang
sudo apt-get install rabbitmq-server  
```  
Enable and start the RabbitMQ service:  
```
sudo systemctl enable rabbitmq-server  
sudo systemctl start rabbitmq-server  
```
Check the status to make sure everything is running smooth:
```
sudo systemctl status rabbitmq-server
```
Open file **configs/my_social_keys.py** and set **CELERY_BROKER_URL** to point your broker url. For example *'amqp://localhost:5672'*.

#### Running Celery 
##### Manually  
```
celery worker -A SZR -l info
celery beat -A SZR -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
##### With Supervisor  
Installation
```
sudo apt-get install supervisor
```
Change files **config/supervisor_celery.sample** and **config/supervisor_celerybeat.sample** to point your local repository 
and copy them to location **/etc/supervisor/conf.d/**  

Reread the configuration and add the new process  
(you need to do this every time functions are changed)  
```
sudo supervisorctl reread
sudo supervisorctl update
```

## Run application
```
make run/dev
```

## GitLab
#### Installation
Instruction for Ubuntu you can find
[here](https://about.gitlab.com/install/#ubuntu)
but you need to install **gitlab-ce** version.
```
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.deb.sh | sudo bash
sudo EXTERNAL_URL="http://localhost" apt-get install gitlab-ce
``` 
#### Configurations
Login in GitLab with admin account. 
Go to gitlab_url/admin/applications and add new application.   
In **Name** write whatever you want.   
In **Redirect URI** write url to authorisation url in your application for example *http<span></span>://localhost:1234/auth/complete/gitlab/*   
Check **Trusted**, **api** and **read_user**.  
Next open file configs/my_social_keys.py and copy **Application ID** to SOCIAL_AUTH_GITLAB_KEY, 
**Secret** to SOCIAL_AUTH_GITLAB_SECRET and set SOCIAL_AUTH_GITLAB_API_URL to point your gitlab url.
