FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Usuario sin privilegios
RUN useradd --system --uid 10001 appuser && chown -R appuser /app
USER 10001

EXPOSE 8005

# API HTTP. El consumidor de eventos usa la misma imagen con: python -m app.consumer
CMD ["gunicorn", "-c", "gunicorn.conf.py", "wsgi:app"]
