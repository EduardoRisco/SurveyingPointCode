#!/bin/bash

# Load environment variables
. ./app-env

docker-compose up -d postgis

until docker exec -it postgis psql --username=${POSTGRES_USER} --dbname=${POSTGRES_DBNAME} -c '\q'; do
	echo "Postgis is uniavaliable...sleeping "
	sleep 1
done

echo "Postgis is up"

docker-compose up -d flask