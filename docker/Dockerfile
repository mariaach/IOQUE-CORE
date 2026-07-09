FROM python:3.13-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY backend/requirements/ /app/requirements/

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    libjpeg62-turbo-dev libwebp-dev libtiff-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements/prod.txt && \
    apt-get purge -y --auto-remove build-essential gcc \
    libjpeg62-turbo-dev libwebp-dev libtiff-dev libfreetype-dev liblcms2-dev libopenjp2-7-dev && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY backend/ /app/
COPY docker/entrypoint.sh /app/docker/entrypoint.sh

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libjpeg62-turbo libwebp7 libtiff6 libfreetype6 liblcms2-2 libopenjp2-7 \
    gosu && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd -r django && useradd -r -g django django

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY --from=builder /app/ /app/

WORKDIR /app

RUN chmod +x /app/docker/entrypoint.sh && \
    chown -R django:django /app

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
