import datetime
from http import HTTPStatus
import uuid

from flask.views import MethodView
from flask_login import login_required
from sqlalchemy import desc
from flask import request, jsonify, Blueprint
from pydantic import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

from adeptum.models import UsersModel, SessionsModel, HistoryPasswordModel, db
from adeptum.schemas import ListUsersModelScheme, UserScheme, AuthorisationScheme, RoleScheme, PasswordScheme
from adeptum.enums import UserRole
from adeptum.decorators import *

bp = Blueprint("users", __name__, url_prefix="/users")


class AdminApi(MethodView):

    decorators = [role_required(UserRole.SUPERUSER.value), login_required]

    def get(self):
        users_from_orm = UsersModel.query.all()
        users = ListUsersModelScheme(users=users_from_orm)
        return users.json(), HTTPStatus.OK

    def post(self):
        data = request.json

        if data is None:
            return jsonify(), HTTPStatus.BAD_REQUEST

        try:
            user_data = UserScheme.parse_obj(data).dict()
        except ValidationError as validation_error:
            return validation_error.json(), HTTPStatus.BAD_REQUEST

        if not UsersModel.query.filter_by(login=user_data['login']).first() is None:
            return jsonify({'massage': "Такой логин уже существует"}), HTTPStatus.BAD_REQUEST

        user = UsersModel(**user_data)
        db.session.add(user)
        db.session.commit()

        history_password = HistoryPasswordModel(user_id=user.id, password=user.password)
        db.session.add(history_password)
        db.session.commit()

        return jsonify(), HTTPStatus.CREATED

    def put(self, user_id, user_property):
        user = UsersModel.query.filter_by(id=user_id).first_or_404()

        if current_user.id == user.id:
            return jsonify(), HTTPStatus.FORBIDDEN

        if user_property == 'role':
            data = request.json

            try:
                new_role = RoleScheme.parse_obj(data).dict()['role']
            except ValidationError as validation_error:
                return validation_error.json(), HTTPStatus.BAD_REQUEST

            if new_role == UserRole.SUPERUSER.value:
                return jsonify(), HTTPStatus.FORBIDDEN

            user.role = new_role.value
        elif user_property == 'block':
            if user.role == UserRole.SUPERUSER.value:
                return jsonify(), HTTPStatus.FORBIDDEN

            user.blocked = True
        else:
            return jsonify(), HTTPStatus.NOT_FOUND

        user.updated_at = datetime.datetime.now()
        db.session.commit()

        return jsonify(), HTTPStatus.OK

    def delete(self, user_id):
        user = UsersModel.query.filter_by(id=user_id).first()

        user.is_deleted = True
        db.session.commit()

        return jsonify(), HTTPStatus.OK


class LoginApi(MethodView):
    def post(self):
        data = request.json

        if data is None:
            return jsonify(), HTTPStatus.BAD_REQUEST

        try:
            user_data = AuthorisationScheme.parse_obj(data).dict()
        except ValidationError as validation_error:
            return validation_error.json(), HTTPStatus.BAD_REQUEST

        user = UsersModel.query.filter_by(login=user_data['login']).first()

        if user is None:
            return jsonify(), HTTPStatus.BAD_REQUEST

        if not check_password_hash(user.password, user_data['password']):
            if user.attempts == 1:
                user.blocked = True

            user.attempts -= 1
            db.session.commit()
            return jsonify(), HTTPStatus.BAD_REQUEST

        if user.blocked:
            return jsonify(), HTTPStatus.FORBIDDEN

        if user.is_deleted:
            return jsonify(), HTTPStatus.BAD_REQUEST

        last_password = HistoryPasswordModel.query.filter_by(password=user.password).first()
        if last_password.updated_at + datetime.timedelta(days=180) < datetime.datetime.now():
            return jsonify({'massage': "Срок действия пароля истёк"}), HTTPStatus.FORBIDDEN

        if user.is_new:
            return jsonify({'massage': "Смените пароль учетной записи"}), HTTPStatus.FORBIDDEN

        user.last_login = datetime.datetime.now()
        token = uuid.uuid4()
        user_session = SessionsModel(
            token=token,
            user_id=user.id,
            expires=datetime.datetime.now() + datetime.timedelta(days=60)
        )

        db.session.add(user_session)
        db.session.commit()

        return jsonify({'token': token}), HTTPStatus.OK

    @login_required
    def put(self, user_id):
        data = request.json

        user = UsersModel.query.filter_by(id=user_id).first_or_404()

        if current_user.id == user_id or current_user.role == UserRole.SUPERUSER.value:
            return jsonify(), HTTPStatus.FORBIDDEN

        try:
            new_password_data = PasswordScheme.parse_obj(data).dict()
        except ValidationError as validation_error:
            return validation_error.json(), HTTPStatus.BAD_REQUEST

        new_password = new_password_data['password']
        old_password = new_password_data['old_password']

        if (not old_password) and current_user.id == user_id:
            return jsonify(), HTTPStatus.BAD_REQUEST

        if current_user.id == user_id:
            if not check_password_hash(user.password, old_password):
                return jsonify(), HTTPStatus.BAD_REQUEST

        massages = list()
        special_characters = set('!@#$%^&*')

        if len(new_password) < 16:
            massages.append('Длина пароля должна быть не менее 16 символов')

        if not len((special_characters & set(new_password))):
            massages.append('В пароле должны специальные символы (@,$,&,*,% и т.п)')

        if len([i for i in new_password if i.isalpha()]) < 2:
            massages.append('Пароль должен содержать минимум 2 символа')

        if old_password:
            for i in range(len(new_password) - 4):
                if new_password[i:i + 4] in old_password:
                    massages.append('Новый пароль не может дублировать более 4 символа подряд из предыдущего пароля')
                    break

        user_old_passwords = HistoryPasswordModel.query.filter_by(user_id=user.id)\
            .order_by(desc(HistoryPasswordModel.created_at)).limit(5).all()

        password_match = any([check_password_hash(password.password, new_password) for password in user_old_passwords])
        if password_match:
            massages.append('Ограничение: новый пароль не должен совпадать, как минимум, с 5 предыдущими паролями')

        if massages:
            return jsonify({'massages': massages}), HTTPStatus.BAD_REQUEST

        new_password_hash = generate_password_hash(new_password)
        user_old_password_history = HistoryPasswordModel.query.filter_by(password=user.password).first()
        user_new_password_history = HistoryPasswordModel(
            user_id=user.id,
            password=new_password_hash
        )

        user.password = new_password_hash
        user.updated_at = datetime.datetime.now()
        if current_user.id == user.id:
            user.is_new = False
        user_old_password_history.is_deleted = True

        db.session.add(user_new_password_history)
        db.session.commit()

        return jsonify(), HTTPStatus.OK


bp.add_url_rule('/', view_func=AdminApi.as_view('users'), methods=['GET'])

bp.add_url_rule('/user', view_func=AdminApi.as_view('registration'), methods=['POST'])

bp.add_url_rule('/user/<user_id>/<user_property>', view_func=AdminApi.as_view('user'), methods=['PUT'])

bp.add_url_rule('/user/<user_id>', view_func=AdminApi.as_view('delete_user'), methods=['DELETE'])

bp.add_url_rule('/user/login', view_func=LoginApi.as_view('login'), methods=['POST'])

bp.add_url_rule('/user/<user_id>', view_func=LoginApi.as_view('change_password'), methods=['PUT'])
