import uuid

from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field, Session, select, Relationship

from db import engine


class TransactionType(SQLModel, table=True):
    __tablename__ = "transaction_types"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    label: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    transactions: list["Transaction"] = Relationship(back_populates="transaction_type")

    @classmethod
    def __declare_last__(cls):
        session = Session(engine)
        transaction_types_exists = session.exec(select(TransactionType)).all()
        if not transaction_types_exists:
            types = [
                TransactionType(name="venta", label="venta"),
                TransactionType(name="compra-de-mercancia", label="compra de mercancia"),
                TransactionType(name="devolucion", label="devolucion"),
                TransactionType(name="pago-de-logistica", label="pago de logistica"),
                TransactionType(name="pago-de-publicidad", label="pago de publicidad"),
                TransactionType(name="embalaje", label="embalaje"),
                TransactionType(name="otro", label="otro"),
            ]
            session.add_all(types)
            session.commit()


class TransactionTypeResponse(SQLModel):
    id: uuid.UUID
    name: str
    label: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
