# How to get this thing to run on an ubuntu aws server to test with canvas online

1. ssh into your aws instance
        ssh -i [~/.ssh/key] [aws_url]

2. clone the repository
        git clone [repo url]

3. create a virtualenv
        virtualenv [name]

4. activate the virtualenv
        source [venv_name]/bin/activate

5. install the requirements for production
        pip install -r requirements.txt
    
6. setup a postgres database
        $ sudo su - postgres
            postgres:~$ psql
                postgres=# create database canvas_course_info;
                postgres=# create user canvas_course_info with password '[PRIVATE]';
            
7. create a secure.py(ATG/TLT structure) or .env (DCE structure) file
    and fill it with the information needed to run the app. Gitignore it.
    If you want the "insert as text" functionality, leave that "offer_text" line.
        SECURE_SETTINGS = {
            'enable_debug' : False,
            'offer_text': True,
            'django_secret_key': '[PRIVATE]',
            'db_default_name': '[DB_NAME]',
            'db_default_user': '[USER_NAME]',
            'db_default_password': '[PRIVATE]',
            'db_default_host': '127.0.0.1',
            'db_default_port': 5432,
            'redis_url': '127.0.0.1:6379',
            'lti_oauth_course_info_consumer_key': '[PRIVATE_KEY]',
            'lti_oath_course_info_consumer_secret': '[PRIVATE_SECRET]',
            'icommons_api_token': '[PRIVATE]',
            'icommons_base_url': 'https://icommons.harvard.edu',
        }

8. Sync the Database
        ./manage.py syncdb
    
9. Run your server in the foreground (case-by case, but gunicorn works well)
        gunicorn -c [GUNICORN_FILE.PY] canvas_course_info.wsgi --bind [AWS_INSTANCE].compute.amazonaws.com --log-file -
    
10. Install on your canvas page: Settings -> Apps -> Add App -> Add by URL
        The key and secret are in your secure.py file
        Config URL:    [AWS_INSTANCE].compute.amazonaws.com:8000/course_info/tool_config
    
11. Party
        Go to Pages -> New Page and you'll see a little blue 'i' as an editor tool. Click it.