from fastapi import FastAPI
from sqlmodel import SQLModel, Session

from db import engine
from models import *
from routers.categories import category_router
from routers.articles import article_router

app = FastAPI(title="Control Stock API", version="0.1",
              description="API para ingreso y salidad de productos en un stock")

app.include_router(category_router)
app.include_router(article_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)
