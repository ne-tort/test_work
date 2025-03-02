FROM python:3.12-slim
COPY ./requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && pip install -r /app/requirements.txt --no-cache-dir
EXPOSE 8000
