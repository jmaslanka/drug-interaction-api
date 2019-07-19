FROM python:3.7-stretch

ENV PYTHONUNBUFFERED 1

RUN apt update && apt-get install -y \
    libpq-dev \
    gcc

WORKDIR /code

COPY requirements.txt /code
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . /code/