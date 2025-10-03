FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 shared-mime-info && pip install --no-cache-dir -r /app/requirements.txt && apt-get remove -y build-essential && rm -rf /var/lib/apt/lists/*
COPY backend/ /app/backend/
WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
