from flask import Flask

import adeptum.config as cnf
from adeptum.blueprints import init_blueprint
from adeptum.errorhandler import init_errorhandler
from adeptum.extensions import init_extensions


def create_app():
    """Запуск приложения"""
    app = Flask(__name__)
    app.config.from_object(cnf)
    # init extension
    init_extensions(app)

    # init blueprint
    init_blueprint(app)

    # init errorhandler
    init_errorhandler(app)

    return app
