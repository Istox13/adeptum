from flask import Blueprint
from flask.views import MethodView

bp = Blueprint("welcome", __name__, url_prefix="/")


class WelcomeApi(MethodView):
    def get(self):
        return "Welcome, Adeptum API"


bp.add_url_rule("/", view_func=WelcomeApi.as_view("welcome"))
