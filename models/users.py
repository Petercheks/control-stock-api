import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str = Field()
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deleted_at: Optional[datetime] = None


class UserCreate(SQLModel):
    username: str
    password: str


class UserBase(SQLModel):
    id: uuid.UUID
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None
