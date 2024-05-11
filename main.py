from fastapi import FastAPI
from sqlmodel import SQLModel

from db import engine

from models import *

app = FastAPI(title="Control Stock API", version="0.1",
              description="API para ingreso y salidad de productos en un stock")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.on_event("startup")
async def startup():
    SQLModel.metadata.create_all(engine)
