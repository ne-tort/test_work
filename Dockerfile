FROM python:3.12-slim
WORKDIR /app
VOLUME ["/pip_cache"]
ENV PIP_CACHE_DIR=/pip_cache
COPY ./requirements.txt /app/

RUN pip install --upgrade pip && pip install -r requirements.txt

EXPOSE 8000
