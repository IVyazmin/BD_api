FROM ubuntu:16.04

MAINTAINER Vyacheslav Kruglov

# Обвновление списка пакетов
RUN apt-get -y update

#
# Установка postgresql
#
ENV PGVER 9.5
RUN apt-get install -y postgresql-$PGVER

# Установка Python3
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install pytz
RUN pip3 install psycopg2
RUN pip3 install gunicorn
RUN pip3 install django

USER postgres

# Create a PostgreSQL role named ``docker`` with ``docker`` as the password and
# then create a database `dbapi` owned by the ``docker`` role.
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER docker WITH SUPERUSER PASSWORD 'docker';" &&\
    createdb -E UTF8 -T template0 -O docker dbapi &&\
    /etc/init.d/postgresql stop

# Adjust PostgreSQL configuration so that remote connections to the
# database are possible.
RUN echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/$PGVER/main/pg_hba.conf

# And add ``listen_addresses`` to ``/etc/postgresql/$PGVER/main/postgresql.conf``
RUN echo "listen_addresses='*'" >> /etc/postgresql/$PGVER/main/postgresql.conf

# Expose the PostgreSQL port
EXPOSE 5432

# Add VOLUMEs to allow backup of config, logs and databases
VOLUME  ["/etc/postgresql", "/var/log/postgresql", "/var/lib/postgresql"]

# Back to the root user
USER root

# Копируем исходный код в Docker-контейнер
ENV WORK /opt/TechnoparkDB
ADD dbAPI/ $WORK/dbAPI/
ADD schema.sql $WORK/schema.sql

# Объявлем порт сервера
EXPOSE 5000

#
# Запускаем PostgreSQL и сервер
#
ENV PGPASSWORD docker
CMD service postgresql start &&\
	psql -h localhost -U docker -d dbapi -f $WORK/schema.sql &&\ 
	cd $WORK/dbAPI &&\ 
	gunicorn -b :5000 dbAPI.wsgi