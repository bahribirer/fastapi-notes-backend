# Python base image
FROM python:3.9-slim

# Çalışma klasörü
WORKDIR /app

# Sistem bağımlılıkları (ör. psycopg2 için)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Gereksinimler
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Ortam değişkenleri (Docker Compose veya Koyeb’de override edeceğiz)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Port (bilgilendirme için)
EXPOSE 8000

# Uvicorn ile başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
