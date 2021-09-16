import datetime
from functools import wraps
from http import HTTPStatus

from flask import abort
from flask_login import current_user

from adeptum.extensions import lm
from adeptum.models import SessionsModel


@lm.request_loader
def load_user_from_request(request):
    authorization_header = request.headers.get('Authorization')

    if authorization_header:
        token = authorization_header.replace('Bearer ', '', 1)

        user_session = SessionsModel.query.filter_by(token=token).first()

        if user_session is None:
            abort(HTTPStatus.UNAUTHORIZED)

        if user_session.is_deleted or user_session.user.blocked:
            abort(HTTPStatus.FORBIDDEN)

        if user_session.expires < datetime.datetime.now() or user_session.user.is_deleted:
            abort(HTTPStatus.UNAUTHORIZED)

        if user_session:
            return user_session.user

    return None


def role_required(*roles):
    def decorator(func):
        wraps(func)

        def new_func(*args, **kwargs):
            if current_user.role not in roles:
                abort(HTTPStatus.FORBIDDEN)

            return func(*args, **kwargs)
        return new_func
    return decorator

