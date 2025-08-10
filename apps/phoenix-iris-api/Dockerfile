FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy only the Iris API into the image context
COPY requirements.txt /app/requirements.txt
COPY dojo_api.py /app/dojo_api.py
COPY dojo_api_optimized.py /app/dojo_api_optimized.py
COPY local_jwt_manager.py /app/local_jwt_manager.py

RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

ENV PORT=8080
CMD ["sh","-c","uvicorn dojo_api:app --host 0.0.0.0 --port $PORT"]


