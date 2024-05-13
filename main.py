import os

from fastapi import FastAPI, Depends
from sqlmodel import SQLModel, Session, select

from db import engine
from models import *
from routers.categories import category_router
from routers.articles import article_router
from auth.login import login_router, manager
from dotenv import load_dotenv
from auth.hasher import Hasher
from models.users import User

load_dotenv()

app = FastAPI(
    title="Control Stock API",
    version="0.1",
    description="API para ingreso y salidad de productos en un stock!"
)

app.include_router(login_router, prefix="/api/v1")
app.include_router(category_router, prefix="/api/v1")
app.include_router(article_router, prefix="/api/v1")


@app.get("/")
async def root(token: str = Depends(manager)):
    return {f"Welcome to Control Stock API {token.username}"}


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)

    session = Session(engine)
    user_exists = session.exec(select(User).where(User.username == "admin")).first()
    if not user_exists:
        user = (User(username=os.getenv("ADMIN"), hashed_password=Hasher.get_password_hash(os.getenv("PWD_ADMIN"))))
        session.add(user)
        session.commit()


@app.on_event("shutdown")
async def shutdown():
    await Session.close()
