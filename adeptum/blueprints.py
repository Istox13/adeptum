from flask import Blueprint

from adeptum.guide.sources import bp as bp_guide
from adeptum.user.sources import bp as bp_user
from adeptum.welcome import bp as bp_welcome

bp_api_v1 = Blueprint("api_v1", __name__, url_prefix="/api/v1")


def init_blueprint(app):
    # group api v1
    bp_api_v1.register_blueprint(bp_user)
    bp_api_v1.register_blueprint(bp_guide)

    # url api v1
    app.register_blueprint(bp_api_v1)
    # welcome
    app.register_blueprint(bp_welcome)

    return app


__all__ = ("init_blueprint",)
