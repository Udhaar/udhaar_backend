FROM python:3.9-buster
COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt
RUN mkdir /src
WORKDIR /src
COPY ./src /src
RUN python manage.py collectstatic --noinput
# RUN python manage.py migrate
RUN useradd -ms /bin/sh user
USER user
