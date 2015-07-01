
# How to get this thing to run on a mac
####TODO: documentation for ATG changes

1. clone the project into ~/dev/ (or whatever)

2. create a new virtual env for project using python 2.7

mkvirtualenv -p/usr/local/bin/python2.7 dce_course_info

If you're not in the right virtualenv switch using workon

(dumdum)Reinhards-MacBook-Pro:dce_course_info reinhard$ workon dce_course_info
(dce_course_info)Reinhards-MacBook-Pro:dce_course_info reinhard$ 

3. install requirements with pip

pip install -r requirements.txt
(also, go to dce_course_info/dce_course_info/requirements, and 
    pip install -r local.txt
    if you're running this offline)

4. make sure postgres is running

on mac:

lunchy start postgres

5. create postgres database and user

Reinhards-MacBook-Pro:dce_course_info reinhard$ psql -d template1
psql (9.3.5)
Type "help" for help.

question: what the hell is template1?

answer: "CREATE DATABASE actually works by copying an existing database.
By default, it copies the standard system database named template1"
http://www.postgresql.org/docs/9.1/static/manage-ag-templatedbs.html

template1=# create database dce_course_info
template1-# ;
CREATE DATABASE
template1=# create user dce_course_info with password 'yabadabadoo';
CREATE ROLE


6. Install redis
brew install redis

6. create a .env file with the variables described in heroku.md
TODO: this may need to be changed to align with secure.py changes

Something like this:

DJANGO_SETTINGS_MODULE=dce_course_info.settings
DJANGO_SECRET_KEY=make_something_actually_secret
LTI_OAUTH_COURSE_INFO_CONSUMER_KEY=your_key
LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET=your_secret
DATABASE_URL=postgres://dce_course_info:password@127.0.0.1:5432/dce_course_info
DJANGO_ADMIN_NAME=somebody
DJANGO_ADMIN_EMAIL=somebody@harvard.edu
DJANGO_SERVER_EMAIL=somebody@harvard.edu
DJANGO_DATABASE_DEFAULT_ENGINE=django_postgrespool
MANDRILL_APIKEY=your_api_key
ICOMMONS_BASE_URL=https://icommons.harvard.edu
ICOMMONS_API_TOKEN=your_api_token
DREST_DEBUG=55
REDIS_URL=http://localhost:6379

Do not stick your .env file in source control. This stuff is sensitive.

7. run syncdb 

python manage.py syncdb


8. Prepare static files

To stick static files where they belong (why is this necessary?) run:

python manage.py collectstatic

9. Run the server -- with a view to testing against local vagrant canvas

When testing against local vagrant canvas install, make sure to bind django to 192.168.50.1

example:

python manage.py runserver 192.168.50.1:8000

Otherwise your canvas on vagrant won't be able to see your django lti app.

This is assuming that your VagrantFile has an entry like this:
                                                                                                                                         
config.vm.network "private_network", ip: "192.168.50.4"
  
I do not understand this, but it works.

Find canvas vagrant box here:

https://github.com/harvard-dce/canvas_vagrant

It will make your LTI developing life much easier.

9b. To run the server with local settings, add "--settings=dce_course_info.settings.local"
    when your run "./manage.py" 
    
    Also, make sure you've gone and run
        pip install -r
  
10. Add LTI tool to canvas
 
 By url -- something like:
 
 http://192.168.50.1:8000/course_info/tool_config
 
 For secret and key see the .env file you created.