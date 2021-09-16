import http

from flask import jsonify


def init_errorhandler(app):
    @app.errorhandler(404)
    def app_page_not_found(e):
        return (
            jsonify(message=str(e)),
            http.HTTPStatus.NOT_FOUND,
        )

    @app.errorhandler(403)
    def app_unauthorized(e):
        return (
            jsonify(message=str(e)),
            http.HTTPStatus.FORBIDDEN,
        )

    @app.errorhandler(401)
    def app_unauthorized(e):
        return (
            jsonify(message=str(e)),
            http.HTTPStatus.UNAUTHORIZED,
        )

    @app.errorhandler(500)
    def app_page_not_found(e):
        return (
            jsonify(message=str(e)),
            http.HTTPStatus.INTERNAL_SERVER_ERROR,
        )
