notepad $PROFILE

add:

function dj {
    docker-compose exec backendsteuerbox python manage.py @args
}

function djpip {
    docker compose exec backendsteuerbox pip @args
}

function djfreeze {
    docker compose exec backendsteuerbox pip freeze > requirements.txt
}
