FROM python:3.11-slim-bookworm

# System dependencies
RUN apt-get update && apt-get install -y \
    locales locales-all \
    default-libmysqlclient-dev gcc pkg-config \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Locale
RUN locale-gen id_ID.UTF-8
ENV LANG=id_ID.UTF-8
ENV LC_ALL=id_ID.UTF-8

WORKDIR /app

# Python dependencies (cloud-specific, no Windows-only packages)
COPY requirements.cloud.txt .
RUN pip install --no-cache-dir -r requirements.cloud.txt

# Copy application
COPY . .
RUN mkdir -p static modules

ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
