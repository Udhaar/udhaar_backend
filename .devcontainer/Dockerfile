FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install --no-install-recommends -y git python3.9 python3.9-dev python3-pip python3-wheel build-essential && \
	apt-get clean && rm -rf /var/lib/apt/lists/*
RUN ln -sf /usr/bin/python3 /bin/python
COPY ./requirements.txt /requirements.txt
RUN pip3 install -r /requirements.txt
RUN mkdir /src
WORKDIR /src
COPY ./src /src
RUN useradd -ms /bin/sh user
USER user
