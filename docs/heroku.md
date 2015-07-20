# Heroku Deployment

####TODO: documentation for ATG changes?
    - We never used heroku with this...

### From scratch

1. Create a new Heroku app. For the purposes of these instructions we'll call it "dce-course-info", but it could really be anything.
2. Install the [heroku-toolbelt](https://toolbelt.heroku.com/).
3. Clone the [canvas_course_info](https://github.com/harvard-dce/canvas_course_info repo).
4. Run `heroku git:remote -a dce-course-info`
5. Add the required heroku add-ons: 
    * [Heroku Postgres](https://addons.heroku.com/heroku-postgresql) 
    * [Mandrill](https://addons.heroku.com/mandrill)
    * [RedisToGo](https://elements.heroku.com/addons/redistogo)
6. Set up the remaining environment vars via `heroku config:set ...` (see below)
7. Run `git push heroku master`. Heroku will detect and build the app.
8. Run `heroku run python manage.py migrate` to initialize the database. 
    * Up to you whether you want to create an admin user. The app doesn't require it.
9. Install the LTI app in the Canvas account settings UI. 
    * Configuration Type: 'By URL'
    * Name: 'Course Info'
    * Consumer Key: value of the **LTI_OAUTH_COURSE_INFO_CONSUMER_KEY** env var
    * Consumer Secret: value of the **LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET** env var
    * Config URL: `https://<app_url>/course_info/tool_config`

### Required env vars

```
LTI_OAUTH_COURSE_INFO_CONSUMER_KEY=...
LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET=...
DJANGO_SECRET_KEY=...
DJANGO_ADMIN_NAME=...
DJANGO_ADMIN_EMAIL=...
DJANGO_SERVER_EMAIL
PYTHONPATH=fakepath
DJANGO_DATABASE_DEFAULT_ENGINE=django_postgrespool
REDIS_URL=...
```

* **LTI_OAUTH_COURSE_INFO_CONSUMER_KEY** and **LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET** are credentials needed during the Canvas LTI app installation. The key should be some simple, identifying string, like "dce-course-admin". For the secret you can probably just use a generated password or a [uuid4](http://en.wikipedia.org/wiki/Universally_unique_identifier#Version_4_.28random.29), but if you want to get fancy there's a [secret key generator](http://techblog.leosoto.com/django-secretkey-generation/) that I sometimes use.
* **DJANGO_SECRET_KEY**: see comments above about the *LTI_OAUTH_COURSE_INFO_CONSUMER_SECRET*.
* **PYTHONPATH**: This is a common kludge to deal with [gunicorn weirdness on heroku](https://github.com/heroku/heroku-buildpack-python/wiki/Troubleshooting#no-module-named-appwsgiapp).
* **DJANGO_ADMIN_NAME** and **DJANGO_ADMIN_EMAIL**: Set these to the name/email of the person or entity that will recieve app error notifications.
* **DJANGO_SERVER_EMAIL**: app error notifications will use this as the "From:" address.
* **REDIS_URL**: copy this from the **REDISTOGO_URL** that was inserted into your heroku config when the redis add-on was added.

### Additional env vars

```
DATABASE_URL=...
MANDRILL_APIKEY=...
MANDRILL_USERNAME=...
```

These are all provided by add-ons; do not set them manually.


