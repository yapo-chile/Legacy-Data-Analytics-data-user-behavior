include scripts/commands/vars.mk

## Deletes all containers
docker-remove: docker-stop
	docker-compose rm -f

## Stops all containers
docker-stop:
	docker-compose stop

## Compiles all the services
docker-build: build
	docker-compose build --no-cache

## Compile and start the service using docker
compose-up: docker-build
	docker-compose up -d

start: compose-up info
	##--scale -d pyms=4 

## Publishes container
docker-publish:
	@scripts/commands/docker-publish.sh

## Execute the service
remove:
	docker stop ${APPNAME}
	docker rm ${APPNAME}

## Compile and start the service
build:
	@scripts/commands/docker-build.sh

## Compile and start the service using docker
reboot: remove build
	docker run -d --name ${APPNAME}  -p ${SERVER_EXPOSED_PORT}:${SERVER_PORT} ${DOCKER_IMAGE}:${BUILD_TAG}

# Installs libraries locally
install:
	pip install -r app/requirements.txt

# Execute style tests
check-style:
	@scripts/commands/check-style.sh