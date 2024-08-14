import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.login import manager
from db import engine
from models.articles import Article
from models.transactions import Transaction, TransactionRequest, TransactionResponse, TypeTransaction, \
    TransactionArticle

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_session():
    with Session(engine) as session:
        yield session


@transaction_router.get("/", response_model=list[TransactionResponse], status_code=200)
async def get_transactions(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    transactions = session.exec(
        select(Transaction)
        .offset(offset)
        .limit(limit)
    ).all()

    transactions_ids = [str(transaction.id.hex) for transaction in transactions]

    articles = session.exec(
        select(Article)
        .join(TransactionArticle, Article.id == TransactionArticle.article_id)
        .where(TransactionArticle.transaction_id.in_(transactions_ids))
    ).all()

    print(articles)

    return transactions


@transaction_router.get("/{id}", response_model=TransactionResponse, status_code=200)
async def get_transaction(*, session: Session = Depends(get_session), id: uuid.UUID):
    transaction = session.exec(select(Transaction).where(Transaction.id == id)).one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@transaction_router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(*, session: Session = Depends(get_session), transaction: TransactionRequest):
    db_transaction = Transaction(**transaction.model_dump())

    if db_transaction.type in [TypeTransaction.SALES, TypeTransaction.SALES, TypeTransaction.MERCHANDISE_PURCHASE]:
        if not transaction.articles:
            raise HTTPException(status_code=400, detail="The articles are required for this transaction")

        register_articles(db_transaction, transaction.articles, session)

    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)
    return db_transaction


def register_articles(transaction: Transaction, articles: List[dict], session: Session):
    transactions_articles = []

    for article in articles:
        article_id = article.get("id")
        article_units = article.get("units")
        transactions_articles.append(
            TransactionArticle(
                id=uuid.uuid4(),
                transaction_id=transaction.id,
                article_id=article_id,
                units=article_units,
            )
        )

    session.add_all(transactions_articles)
    session.commit()


@transaction_router.delete("/{id}")
def delete_category(*, session: Session = Depends(get_session), id: uuid.UUID):
    transaction = session.get(Transaction, id)

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    session.delete(transaction)
    session.commit()
    return {"message": "Transaction deleted"}
