from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: int = Field(default=None, primary_key=True)
    name: str
    code: str
    units: int
    purchase_price: float
    sale_price: float
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    category_id: int | None = Field(default=None, foreign_key="categories.id")
