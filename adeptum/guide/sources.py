import http

from flask import Blueprint, jsonify
from flask.views import MethodView
from flask_login import login_required

bp = Blueprint("guide", __name__, url_prefix="/guide")


class CompanyApi(MethodView):
    decorators = [login_required]

    def __init__(self):
        pass

    def get(self):
        pass

    def post(self):
        return jsonify(message=http.HTTPStatus.CREATED.phrase), http.HTTPStatus.CREATED

    def put(self):
        return jsonify(message=http.HTTPStatus.OK.phrase), http.HTTPStatus.OK

    def delete(self):
        return jsonify(message=http.HTTPStatus.OK.phrase), http.HTTPStatus.OK


bp.add_url_rule(
    "/companies", view_func=CompanyApi.as_view("companies"), methods=["GET", "POST"]
)

bp.add_url_rule(
    "/companies/<id>",
    view_func=CompanyApi.as_view("company"),
    methods=["PUT", "DELETE"],
)
