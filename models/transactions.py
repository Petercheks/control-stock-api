import uuid

from datetime import datetime
from typing import Optional

from enum import Enum
from sqlmodel import SQLModel, Field



class TypeTransaction(str, Enum):
    SALES = "sales"
    MERCHANDISE_PURCHASE = "merchandise_purchase"
    LOGISTCS_PAYMENT = "logistics_payment"
    ADVERTISMENTS_PAYMENT = "advertisments_payment"
    PACKINGS = "packings"
    OTHER = "other"
    RETURNS = "returns"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    type: TypeTransaction
    amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None


class TransactionArticle(SQLModel, table=True):
    __tablename__ = "transactions_articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_id: uuid.UUID = Field(foreign_key="transactions.id")
    article_id: uuid.UUID = Field(foreign_key="articles.id")
    units: int


class TransactionRequest(SQLModel):
    type: TypeTransaction
    amount: float
    description: Optional[str] = None
    articles: Optional[list] = None


class TransactionResponse(SQLModel):
    id: uuid.UUID
    type: TypeTransaction
    amount: float
    description: Optional[str] = None
    articles: Optional[list[dict]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
