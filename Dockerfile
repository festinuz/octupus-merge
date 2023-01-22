FROM python:3-alpine

RUN apk add --no-cache git

RUN pip install requests

ADD . /app
WORKDIR /app
# ENV PYTHONPATH /app

ENTRYPOINT ["python", "/app/main.py"]
