DB_HOST = localhost
DB_PORT = 5432
DB_NAME = hasker_db
DB_USER = hasker_db_user 
DB_PASSWORD = hasker_db_user_pass

DOCKER_DB_VOLUME = hasker_db_volume

build:
	sudo docker run -p $(DB_PORT):$(DB_PORT) -d --name $(DB_NAME) -v $(DOCKER_DB_VOLUME):/var/lib/postgresql/data postgres:9.6
	@while ! pg_isready -h $(DB_HOST) -p $(DB_PORT) > /dev/null 2> /dev/null; do\
		echo "Waiting for postgres $(DB_NAME) container to start ...";\
		sleep 10;\
		done
	psql -h $(DB_HOST) -U postgres -c "CREATE DATABASE $(DB_NAME);"
	psql -h $(DB_HOST) -U postgres -c "CREATE USER $(DB_USER) WITH PASSWORD '$(DB_PASSWORD)';"
	psql -h $(DB_HOST) -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $(DB_NAME) TO $(DB_USER);"
	sudo docker build -t hasker .

dev:
	@if pg_isready -h $(DB_HOST) -p $(DB_PORT) > /dev/null 2> /dev/null; then\
		sudo docker run -it --rm --net=host hasker /bin/bash -c "python3 /opt/hasker/manage.py migrate && python3 /opt/hasker/manage.py runserver";\
	else\
		echo "run: make clean --ignore-errors && make build";\
	fi

test:
	@if pg_isready -h $(DB_HOST) -p $(DB_PORT) > /dev/null 2> /dev/null; then\
		psql -h $(DB_HOST) -U postgres -c "ALTER USER $(DB_USER) CREATEDB;";\
		sudo docker run -it --rm --net=host hasker /bin/bash -c "python3 /opt/hasker/manage.py test hasker -v 2";\
	else\
		echo "run: make clean --ignore-errors && make build";\
	fi

clean:
	sudo docker container stop $(DB_NAME)
	sudo docker container rm $(DB_NAME)
	sudo docker volume rm $(DOCKER_DB_VOLUME)