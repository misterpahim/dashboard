
FROM python:3.11-slim
WORKDIR /app
COPY config/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
COPY app /app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
