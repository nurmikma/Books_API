FROM python:3.8-slim

LABEL maintainer="Python"
LABEL description="See on minu Python Docker pilt"
LABEL version="3-alpine"

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN mkdir raamatud

COPY . /usr/src/app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt

COPY hs9-flask-api-raamatute-otsing.py app.py

EXPOSE 5000

CMD ["python3", "app.py"]
