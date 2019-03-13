![Logo](https://github.com/EduardoRisco/SurveyingPointCode/blob/master/Docs/Logo/Logo_spc.png)

# Surveying Point Code
Allows to automate the delineation process in CAD, by coding points in a topographic survey.

![Iconos](https://github.com/EduardoRisco/SurveyingPointCode/blob/master/Docs/Logo/Transf_opt.png)

------

Instrucciones configuración entorno:

- Instalación de Docker.


- Descargar imagenes contenedores, uno  de PostgreSQL con en módulo espacial PostGis  y otro con PgAdmin4, para administrar la BBDD.

   *docker pull mdillon/postgis*

   *docker pull dpage/pgadmin4*

- Crear volumenes para la garantizar la persistencia de datos.

  *docker volume create  --driver local --name=pg_data*
  *docker volume create --driver local --name=pga4volume*


- Crear una conexion para comunicar los contenedores.

  *docker network create --driver bridge pgnetwork*

- Arrancar el contenedor PostgreSQL con los siguientes parametros:

  *docker run --name=postgis --hostname=postgres --network=pgnetwork -d -e POSTGRES_USER=tfg -e POSTGRES_PASS=f04f1b4d7734f0dc3c4da46f19c0a9f49b56 -e POSTGRES_DBNAME=spcode -e ALLOW_IP_RANGE=0.0.0.0/0 -p 5432:5432 -v pg_data:/var/lib/postgresql --restart=always mdillon/postgis*

- Arrancar el contenedor PgAdmin4 con los siguientes parametros:

  *docker run --publish 80:80 --volume=pga4volume:/var/lib/pgadmin --name=pgadmin4 --hostname=pgadmin4 --network=pgnetwork --detach -e "PGADMIN_DEFAULT_EMAIL=email@gmail.com" -e "PGADMIN_DEFAULT_PASSWORD=tfg" -d dpage/pgadmin4*

