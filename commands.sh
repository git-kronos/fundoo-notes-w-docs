#! /bin/bash

arg=$1


<<command
mkdir project && cd project
django-admin startproject project .
mkdir -p app/func_one
python manage.py startapp func_one app/func_one
python manage.py runserver ip:port
command

case $arg in
init) pip install -r ./requirements.txt;;
run) python manage.py runserver;;
app)
    read -p 'name: ' name
    read -p 'path: ' path

    if [ ! -z "$name" ] && [ ! -z "$path" ]; then
        dir="$path/$name"
        mkdir -p $dir
        python manage.py startapp $name $dir
    elif [ -z "$name" ]; then
        echo 'app `name` is required'
    elif [ -z "$path" ]; then
        python manage.py startapp $name
        echo "app is created at `pwd`"
    fi

    ;;
migrate)
    python manage.py makemigrations
    python manage.py migrate
    ;;
user) python manage.py createsuperuser --email admin@email.com;;
*) echo 'Error: Wrong arguments';;
esac
