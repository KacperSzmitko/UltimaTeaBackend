FROM python:3.8.5


RUN pip install --upgrade pip
RUN apt-get -y update && apt-get -y install libpq-dev && apt-get -y install python-dev

COPY ./requirements.txt .
RUN pip install -r requirements.txt

COPY ./ultima_tea /app

WORKDIR /app

COPY ./entrypoint.sh /
ENTRYPOINT ["sh", "/entrypoint.sh"]

