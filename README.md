# Python: Digital Advance :)

Proyecto de integración e-commerce alumnos de Duoc UC.

Para poder ejecutar el proyecto de forma local realice lo siguiente:
(No se olvide de cambiar el procfile por el de windows)http://prntscr.com/jqh959
```sh
$ git clone git@github.com:heroku/python-getting-started.git
$ cd python-getting-started

$ pip install pipenv

$ python manage.py migrate
$ python manage.py collectstatic

$ heroku local
```

Tu aplicación ahora debería estar ejecutándose en  [localhost:5000](http://localhost:5000/).

## Para poder subirlo a heroku es necesesario ejecutar lo siguiente:

(No se olvide de cambiar el procfile por el de linux)http://prntscr.com/jqh959

```sh
$ heroku create
$ heroku config:set DISABLE_COLLECTSTATIC=1
$ git push heroku master
$ heroku run 'bower install --config.interactive=false;grunt prep;python manage.py collectstatic --noinput'
$ heroku config:unset DISABLE_COLLECTSTATIC   
$ heroku run python manage.py collectstatic 


$ heroku run python manage.py makemigrations
$ heroku run python manage.py migrate
$ heroku open
```
or

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

## Documentation
https://trello.com/b/ljK5oACP/tablero-kanban-brian-rojas-villegas

Create by Franco Fernandez and Elias Alveal.

Managed by Brian Rojas.