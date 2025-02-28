FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY ./test_app/ /app/test_app/

EXPOSE 8000

CMD ["uvicorn", "test_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
