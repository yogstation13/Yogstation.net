FROM tiangolo/uwsgi-nginx:python3.9

ENV UWSGI_INI /srv/www/yogsite/uwsgi.ini

COPY . /srv/www/yogsite
COPY nginx.conf /app/nginx.conf

RUN apt-get update
RUN apt-get install -y ffmpeg

RUN pip install -r /srv/www/yogsite/requirements.txt

WORKDIR /srv/www/yogsite
