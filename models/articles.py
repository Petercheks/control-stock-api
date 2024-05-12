import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel
from .categories import Category


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False)
    name: str
    code: str
    units: int
    purchase_price: float
    sale_price: float
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    category_id: int | None = Field(default=None, foreign_key="categories.id")


class ArticleWithCategory(Article):
    category: Category | None = None
