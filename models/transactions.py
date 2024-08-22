import uuid

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship

from models.transaction_types import TransactionType, TransactionTypeResponse


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    transaction_type_id: uuid.UUID | None = Field(default=None, foreign_key="transaction_types.id")
    transaction_type: Optional[TransactionType] = Relationship(back_populates="transactions")


class TransactionArticle(SQLModel, table=True):
    __tablename__ = "transactions_articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    transaction_id: uuid.UUID = Field(foreign_key="transactions.id")
    article_id: uuid.UUID = Field(foreign_key="articles.id")
    units: int


class TransactionRequest(SQLModel):
    transaction_type_id: uuid.UUID
    amount: float
    description: Optional[str] = None
    articles: Optional[list] = None


class TransactionResponse(SQLModel):
    id: uuid.UUID
    transaction_type: TransactionTypeResponse
    amount: float
    description: Optional[str] = None
    articles: Optional[list[dict]] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
