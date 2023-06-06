FROM python:3.9-slim-buster

# layer caching for faster builds
RUN pip install celery[librabbitmq] influxdb-client pydantic[dotenv,email] pydash python-decouple

#COPY app.py /app.py
ADD . /queue
WORKDIR /queue

ENTRYPOINT celery -A tasks worker --loglevel=info
