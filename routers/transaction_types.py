import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from auth.login import manager
from db import engine
from models.transaction_types import TransactionType, TransactionTypeResponse

transaction_type_router = APIRouter(prefix="/transaction-types", tags=["transaction-types"])


def get_session():
    with Session(engine) as session:
        yield session


@transaction_type_router.get("/", response_model=list[TransactionTypeResponse], status_code=200)
async def get_articles(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    return session.exec(
        select(TransactionType).offset(offset).limit(limit)
    ).all()
