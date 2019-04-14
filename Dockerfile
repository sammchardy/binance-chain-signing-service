FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./app /app
COPY ./config /config

RUN apt-get update
RUN apt-get install -y build-essential automake pkg-config libtool libffi-dev libgmp-dev python-dev libssl-dev libsecp256k1-dev

RUN pip install -r /app/requirements.txt

# gunicorn log level
ENV LOG_LEVEL info
