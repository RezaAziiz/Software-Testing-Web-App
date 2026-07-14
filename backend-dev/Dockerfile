FROM python:3.11-slim-bookworm

# System dependencies + Java 17 for Jacoco Engine
RUN apt-get update && apt-get install -y \
    locales locales-all \
    default-libmysqlclient-dev gcc pkg-config \
    openjdk-17-jdk \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME secara eksplisit agar Gradle wajib pakai Java 17
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

# Locale
RUN locale-gen id_ID.UTF-8
ENV LANG=id_ID.UTF-8
ENV LC_ALL=id_ID.UTF-8

WORKDIR /app

# Python dependencies (cloud-specific, no Windows-only packages)
COPY requirements.cloud.txt .
RUN pip install --no-cache-dir -r requirements.cloud.txt

# Copy application + jacoco engine
COPY . .
RUN mkdir -p static

# Verify Java is available and print version to check
RUN java -version && echo "JAVA_HOME is set to $JAVA_HOME"

# Make gradlew executable
RUN chmod +x jacoco-engine/gradlew || true

# Pre-download and cache Gradle wrapper and dependencies (Solusi 1)
RUN cd jacoco-engine && ./gradlew test --no-daemon

# Cloud Run uses PORT env var
ENV PORT=8080
EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]