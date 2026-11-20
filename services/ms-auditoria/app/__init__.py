from flask import Flask

from .config import Config
from .extensions import db
from .observabilidad import configurar_logging, registrar_errores, registrar_middleware


def create_app(overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if overrides:
        app.config.update(overrides)

    configurar_logging(app.config["LOG_LEVEL"], app.config["SERVICE_NAME"])
    db.init_app(app)

    from .routes import bp

    app.register_blueprint(bp)
    registrar_middleware(app)
    registrar_errores(app)

    if app.config["AUTO_CREATE_TABLES"]:
        from . import models  # noqa: F401  (registra los modelos antes de create_all)

        with app.app_context():
            db.create_all()

    return app
