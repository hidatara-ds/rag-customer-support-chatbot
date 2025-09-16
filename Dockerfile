FROM python:3.11-slim

WORKDIR /app

# System deps (opsional): default cukup ringan
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential default-mysql-client && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY frontend/ frontend/
# data/ tidak perlu di image produksi, tapi kalau mau demo bisa ikut
# COPY data/ data/

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
