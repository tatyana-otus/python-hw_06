# Hasker

## local_settings.py
local_settings overrides settings specific to the local environment, especially DATABASES, SECRET_KEY, ALLOWED_HOSTS and DEBUG variables

local_settings.py.example example of local_settings.py

## Usage for test and demo 
```
git clone https://github.com/tatyana-otus/python-hw_06.git ./hasker
cd hasker
make build
make test
make dev
```

## Usage with nginx and uwsgi
```
git clone https://github.com/tatyana-otus/python-hw_06.git ./hasker
cd hasker
make build
make nginx
```

Go to 'http://0.0.0.0:8000/' in your browser, and you should see something like Q&A site.