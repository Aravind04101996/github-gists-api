FROM python:3.13-alpine as builder
WORKDIR /gists
COPY requirements.txt .

RUN apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers && \
    python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/venv -type f -name '*.pyc' -delete && \
    find /opt/venv -type f -name '*.pyo' -delete && \
    apk del .build-deps

FROM python:3.13-alpine

RUN apk add --no-cache wget && \
    adduser -D -u 1000 gistsuser && \
    mkdir -p /gists && \
    chown -R gistsuser:gistsuser /gists

WORKDIR /gists

COPY --from=builder /opt/venv /opt/venv
COPY --chown=gistsuser:gistsuser main.py .
COPY --chown=gistsuser:gistsuser templates/ ./templates/

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \ 
    PYTHONDONTWRITEBYTECODE=1

USER gistsuser
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=2).read()" || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "60", "main:app"]