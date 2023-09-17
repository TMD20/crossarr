FROM python:3.11-alpine
RUN apk add --no-cache tini

RUN mkdir /app
COPY /arr /app/arr/
COPY /setup /app/setup/
COPY *.py /app/
COPY requirements.txt /app/requirements.txt
RUN pip3.11 install -r /app/requirements.txt

RUN mkdir /config
RUN mkdir /logs


WORKDIR /app
VOLUME /config
ENV CROSSARR_DOCKER TRUE
ENTRYPOINT ["tini", "--","/app/app.py"]

