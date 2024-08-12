import uuid

from datetime import datetime
from typing import Optional

from sqlalchemy import Enum
from sqlmodel import SQLModel, Field


class TypeTransaction(str, Enum):
    SALES = "sales"
    MERCHANDISE_PURCHASE = "merchandise_purchase"
    LOGISTCS_PAYMENT = "logistics_payment"
    ADVERTISMENTS_PAYMENT = "advertisments_payment"
    PACKINGS = "packings"
    OTHER = "other"


class Transaction(SQLModel, table=True):
    __tablename__ = "transactions"

    id: uuid.UUID = Field(default=uuid.UUID(), primary_key=True)
    type: TypeTransaction = Field(Enum(TypeTransaction))
    amount: float
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None
