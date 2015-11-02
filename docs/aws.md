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
    (see canvas_course_info/settings/secure.py.example for the list of keys) 

8. Sync the Database
        ./manage.py syncdb
    
9. Run your server in the foreground (case-by case, but gunicorn works well)
        gunicorn -c [GUNICORN_FILE.PY] canvas_course_info.wsgi --bind [AWS_INSTANCE].compute.amazonaws.com --log-file -
    
10. Install on your canvas page: Settings -> Apps -> Add App -> Add by URL
        The key and secret are in your secure.py file
        Config URL:    [AWS_INSTANCE].compute.amazonaws.com:8000/course_info/tool_config
    
11. Party
        Go to Pages -> New Page and you'll see a little blue 'i' as an editor tool. Click it.