import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import update
from sqlmodel import Session, select

from auth.login import manager
from db import engine
from models.articles import Article
from models.transaction_types import TransactionType
from models.transactions import Transaction, TransactionRequest, TransactionResponse, TransactionArticle

transaction_router = APIRouter(prefix="/transactions", tags=["transactions"])


def get_session():
    with Session(engine) as session:
        yield session


SALES = "venta"
MERCHANDISE_PURCHASE = "compra-de-mercancia"


@transaction_router.get("/", response_model=list[TransactionResponse], status_code=200)
async def get_transactions(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    transactions = session.exec(
        select(Transaction)
        .join(Transaction.transaction_type)
        .offset(offset)
        .limit(limit)
    ).all()

    transactions_ids = [str(transaction.id.hex) for transaction in transactions]

    articles_in_transactions = session.exec(
        select(
            Article.id,
            Article.name,
            TransactionArticle.units,
            TransactionArticle.article_id,
            TransactionArticle.transaction_id
        )
        .join(TransactionArticle, Article.id == TransactionArticle.article_id)
        .where(TransactionArticle.transaction_id.in_(transactions_ids))
    ).all()

    transactions_response = []
    for transaction in transactions:
        articles_transaction = []
        for article in articles_in_transactions:
            if transaction.id == article.transaction_id:
                articles_transaction.append({
                    "id": article.article_id,
                    "name": article.name,
                    "units": article.units
                })

        transactions_response.append(TransactionResponse(
            id=transaction.id,
            transaction_type=transaction.transaction_type.model_dump(),
            amount=transaction.amount,
            description=transaction.description,
            articles=articles_transaction,
            created_at=transaction.created_at,
            updated_at=transaction.updated_at,
            deleted_at=transaction.deleted_at
        ))

    return transactions_response


@transaction_router.get("/{id}", response_model=TransactionResponse, status_code=200)
async def get_transaction(*, session: Session = Depends(get_session), id: uuid.UUID):
    transaction = session.exec(
        select(Transaction).join(Transaction.transaction_type).where(Transaction.id == id)).one_or_none()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    articles_in_transaction = session.exec(
        select(
            Article.id,
            Article.name,
            TransactionArticle.units,
            TransactionArticle.article_id,
            TransactionArticle.transaction_id
        )
        .join(TransactionArticle, Article.id == TransactionArticle.article_id)
        .where(TransactionArticle.transaction_id == transaction.id)
    ).all()

    return TransactionResponse(
        id=transaction.id,
        transaction_type=transaction.transaction_type.model_dump(),
        amount=transaction.amount,
        description=transaction.description,
        articles=[
            {"id": article.id, "name": article.name, "units": article.units} for article in articles_in_transaction
        ],
        created_at=transaction.created_at,
        updated_at=transaction.updated_at,
        deleted_at=transaction.deleted_at
    )


@transaction_router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(*, session: Session = Depends(get_session), transaction: TransactionRequest):
    db_transaction = Transaction(**transaction.model_dump())
    session.add(db_transaction)
    session.commit()
    session.refresh(db_transaction)

    types_with_products = session.exec(
        select(TransactionType.id)
        .where(TransactionType.name.in_([SALES, MERCHANDISE_PURCHASE]))
    ).all()

    if db_transaction.transaction_type_id in types_with_products:
        if not transaction.articles:
            raise HTTPException(status_code=400, detail="The articles are required for this transaction")

        register_articles(db_transaction, transaction.articles, session)

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

        transaction_type_sale_id = session.exec(select(TransactionType.id).where(TransactionType.name == SALES)).one()
        transaction_type_sell_id = session.exec(
            select(TransactionType.id).where(TransactionType.name == MERCHANDISE_PURCHASE)).one()

        quantity = None
        if transaction.transaction_type_id == transaction_type_sale_id:
            quantity = - article_units

        if transaction.transaction_type_id == transaction_type_sell_id:
            quantity = article_units

        if quantity:
            session.exec(
                update(Article)
                .where(Article.id == article_id)
                .values(units=Article.units + quantity)
            )
            session.commit()

    session.add_all(transactions_articles)
    session.commit()
