import os

bind = f"0.0.0.0:{os.getenv('SERVICE_PORT', '8007')}"
workers = int(os.getenv("GUNICORN_WORKERS", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))
timeout = 30
graceful_timeout = 20
errorlog = "-"
accesslog = None


def on_starting(server):
    from app.config import config_dict
    from app.consul import registrar
    registrar(config_dict())


def on_exit(server):
    from app.config import config_dict
    from app.consul import desregistrar
    desregistrar(config_dict())
