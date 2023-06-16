FROM python:3.11.1-slim-bullseye
RUN apt update && apt install -y build-essential

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

# add requirements.txt and startup scripts to the image
COPY requirements.txt /code/

# check if we have known security issues (CVE) in the dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code

EXPOSE 8000
