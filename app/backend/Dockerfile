FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    NLTK_DATA=/usr/local/share/nltk_data

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir azure-cognitiveservices-speech

# Download NLTK data (add this after pip install)
RUN python -m nltk.downloader -d /usr/local/share/nltk_data \
    punkt \
    stopwords \
    vader_lexicon

# Download spaCy model (add this)
RUN python -m spacy download en_core_web_sm

COPY . .

# Create db_dir directory
RUN mkdir -p db_dir && chmod 755 db_dir

EXPOSE 8086

# Use gunicorn with eventlet workers for SocketIO compatibility
CMD ["gunicorn", "--worker-class", "eventlet", "--workers", "1", "--bind", "0.0.0.0:8086", "--timeout", "300", "--graceful-timeout", "30", "--access-logfile", "-", "--error-logfile", "-", "--log-level", "info", "main:app"]

