import uuid

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from .categories import CategoryBase, Category


class Article(SQLModel, table=True):
    __tablename__ = "articles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    units: int
    image: str
    description: str
    purchase_price: float
    sale_price: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None
    student: str

    category_id: uuid.UUID | None = Field(default=None, foreign_key="categories.id")
    category: Optional[Category] = Relationship(back_populates="articles")


class ArticleCreate(SQLModel):
    name: str
    units: int
    image: str
    description: str
    purchase_price: float
    sale_price: Optional[float] = None
    category_id: uuid.UUID | None = None
    student: str


class ArticleBase(SQLModel):
    id: uuid.UUID
    category: Optional[CategoryBase] = None
    name: str
    units: int
    image: str
    description: str
    purchase_price: float
    sale_price: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
    student: str
