import uuid

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None

    articles: list["Article"] = Relationship(back_populates="category")


class CategoryCreate(SQLModel):
    name: str


class CategoryBase(SQLModel):
    id: uuid.UUID
    name: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class CategoryResponse(CategoryBase):
    linked_products_count: int
