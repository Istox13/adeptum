import datetime
from uuid import UUID
from typing import List, Optional

from pydantic import BaseModel

from adeptum.enums import UserRole


class AdeptumModelScheme(BaseModel):
    id: UUID
    is_deleted: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True


class UsersModelScheme(AdeptumModelScheme):
    login: str
    first_name: str
    last_name: str
    patronymic: str
    role: str
    password: str
    attempts: str
    last_login: datetime.datetime
    blocked: bool


class PasswordHistoryModelScheme(AdeptumModelScheme):
    user_id: UUID
    password: str

    class Config:
        orm_mode = True


class SessionsModelScheme(AdeptumModelScheme):
    user_id: UUID
    token: str
    expires: datetime.datetime

    class Config:
        orm_mode = True


class ListUsersModelScheme(BaseModel):
    users: List[UsersModelScheme]


class UserScheme(BaseModel):
    login: str
    first_name: str
    last_name: str
    patronymic: str


class AuthorisationScheme(BaseModel):
    login: str
    password: str


class RoleScheme(BaseModel):
    role: UserRole


class PasswordScheme(BaseModel):
    password: str
    old_password: Optional[str]
