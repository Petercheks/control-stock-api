import os

from fastapi import Depends, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_login import LoginManager

from fastapi_login.exceptions import InvalidCredentialsException
from sqlmodel import Session, select

from auth.hasher import Hasher
from db import engine
from models.users import User

SECRET = os.getenv("SECRET_KEY")
manager = LoginManager(SECRET, "api/v1/login")

login_router = APIRouter(prefix="/login", tags=["auth"])


@manager.user_loader()
def query_user(username: str):
    session = Session(engine)
    return session.exec(select(User).where(User.username == username)).first()


@login_router.post("")
def login(data: OAuth2PasswordRequestForm = Depends()):
    username = data.username
    password = data.password

    user = query_user(username)
    if not user:
        raise InvalidCredentialsException
    elif Hasher.verify_password(password, user.hashed_password) is False:
        raise InvalidCredentialsException

    access_token = manager.create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
