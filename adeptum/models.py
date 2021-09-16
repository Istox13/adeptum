import uuid

from flask_login import UserMixin
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash

from adeptum.extensions import db
from adeptum.enums import UserRole


class AdeptumModel(db.Model):
    """Parent Adeptum Model"""

    __abstract__ = True

    id = sa.Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        default=uuid.uuid4,
        comment="Идентификатор",
    )

    is_deleted = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        comment="Удалено?",
    )

    created_at = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.current_timestamp(),
        comment="Дата создания",
    )

    updated_at = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
        comment="Дата обновления",
    )

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.id)


class UsersModel(AdeptumModel, UserMixin):

    __tablename__ = "users"

    login = sa.Column(
        sa.VARCHAR,
        nullable=False,
        default=False,
        comment="Логин пользователя"
    )

    first_name = sa.Column(
        sa.VARCHAR,
        nullable=False,
        comment="Имя пользователя"
    )

    last_name = sa.Column(
        sa.VARCHAR,
        nullable=False,
        comment="Фамилия пользователя"
    )

    patronymic = sa.Column(
        sa.VARCHAR,
        nullable=False,
        comment="Отчество пользователя"
    )

    role = sa.Column(
        sa.VARCHAR,
        nullable=False,
        default=UserRole.NEW_USER.value,
        comment="""Роль пользователя:
                user1 - Ответственный за логистическое обеспечение
                user2 - Ответственный за регистрацию фактов затрат
                superuser - Функциональный администратор системы"""
    )

    password = sa.Column(
        sa.VARCHAR,
        nullable=False,
        default=generate_password_hash("ChAnGe0%0Me@PlS&"),
        comment="Пароль пользователя"
    )

    attempts = sa.Column(
        sa.Integer,
        nullable=False,
        default=3,
        comment="Попытки входа пользователя"
    )

    last_login = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
        comment="Дата обновления",
    )

    blocked = sa.Column(
        sa.Boolean,
        nullable=False,
        default=False,
        comment="Заблокированно?",
    )

    is_new = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True,
        comment="Новый пользователь?",
    )


class HistoryPasswordModel(AdeptumModel):

    __tablename__ = "history_password"

    user_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey(UsersModel.id),
        nullable=False,
        comment="Идентификатор пользователя"
    )

    password = sa.Column(
        sa.VARCHAR,
        nullable=False,
        comment="Пароль пользователя"
    )


class SessionsModel(AdeptumModel):

    __tablename__ = "sessions"

    user_id = sa.Column(
        UUID(as_uuid=True),
        sa.ForeignKey(UsersModel.id),
        nullable=False,
        comment="Идентификатор пользователя"
    )

    token = sa.Column(
        sa.VARCHAR(1000),
        nullable=False,
        comment="Токен пользователя"
    )

    expires = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.current_timestamp(),
        onupdate=sa.func.current_timestamp(),
        comment="Дата конца времени жизни токена"
    )

    user = db.relationship('UsersModel', backref=db.backref('sessions'))
