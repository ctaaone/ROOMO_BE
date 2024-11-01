FROM postgres:latest

COPY init.sql /docker-entrypoint-initdb.d/

RUN apt-get update && apt-get install -y postgis postgresql-$PG_MAJOR-postgis-$POSTGIS_MAJOR && \
    rm -rf /var/lib/apt/lists/*
