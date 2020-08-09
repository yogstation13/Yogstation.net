FROM tiangolo/uwsgi-nginx:python3.8

ENV UWSGI_INI /srv/www/yogsite/uwsgi.ini

COPY . /srv/www/yogsite
COPY nginx.conf /etc/nginx/sites-available/ 

RUN pip install -r /srv/www/yogsite/requirements.txt

WORKDIR /srv/www/yogsite