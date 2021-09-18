FROM tiangolo/uwsgi-nginx:python3.8

ENV UWSGI_INI /srv/www/yogsite/uwsgi.ini

COPY . /srv/www/yogsite
COPY nginx.conf /app/nginx.conf

RUN echo "deb http://deb.debian.org/debian testing main" >>  /etc/apt/sources.list
RUN echo "deb http://deb.debian.org/debian sid main" >>  /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y libcrypt1
RUN apt-get install -y -t testing ffmpeg

RUN pip install -r /srv/www/yogsite/requirements.txt

WORKDIR /srv/www/yogsite
