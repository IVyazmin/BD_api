FROM ubuntu:16.04

MAINTAINER VIV

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

# Create a PostgreSQL role named ``viv`` with ``sunmoonmars`` as the password and
# then create a database `poststest` owned by the ``viv`` role.
RUN /etc/init.d/postgresql start &&\
    psql --command "CREATE USER viv WITH SUPERUSER PASSWORD 'sunmoonmars';" &&\
    createdb -E UTF8 -T template0 -O viv poststest &&\
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
ENV WORK /opt/BD
ADD posts/ $WORK/posts/
ADD bd_init.sql $WORK/bd_init.sql

# Объявлем порт сервера
EXPOSE 5000

#
# Запускаем PostgreSQL и сервер
#
ENV PGPASSWORD sunmoonmars
CMD service postgresql start &&\
	psql -h localhost -U viv -d poststest -f $WORK/bd_init.sql &&\ 
	cd $WORK/posts &&\ 
	gunicorn -b :5000 posts.wsgi
