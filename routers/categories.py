import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select

from auth.login import manager
from db import engine
from models.articles import Article
from models.categories import Category, CategoryResponse, CategoryCreate, CategoryBase

category_router = APIRouter(prefix="/categories", tags=["categories"])


def get_session():
    with Session(engine) as session:
        yield session


@category_router.get("/", response_model=list[CategoryResponse], status_code=200)
async def get_categories(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    return session.exec(
        select(
            Category.id,
            Category.name,
            Category.created_at,
            Category.updated_at,
            func.count(Article.id).label("linked_products_count")
        )
        .join(Article, isouter=True)
        .group_by(Category.id)
        .offset(offset)
        .limit(limit)
    ).all()


@category_router.get("/{id}", response_model=CategoryResponse, status_code=200)
async def get_category(*, session: Session = Depends(get_session), id: uuid.UUID):
    category = session.exec(
        select(
            Category.id,
            Category.name,
            Category.created_at,
            Category.updated_at,
            func.count(Article.id).label("linked_products_count")
        )
        .join(Article, isouter=True)
        .where(Category.id == id)
    ).one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@category_router.post("/", response_model=CategoryBase, status_code=201)
async def create_category(*, session: Session = Depends(get_session), category: CategoryCreate):
    db_category = Category(**category.dict())
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@category_router.patch("/{id}", response_model=CategoryBase, status_code=200)
async def update_category(*, session: Session = Depends(get_session), id: uuid.UUID, category: CategoryCreate):
    db_category = session.get(Category, id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")
    category_data = category.model_dump(exclude_unset=True)
    for key, value in category_data.items():
        setattr(db_category, key, value)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


@category_router.delete("/{id}")
def delete_category(*, session: Session = Depends(get_session), id: uuid.UUID):
    category = session.get(Category, id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    session.delete(category)
    session.commit()
    return {"message": "Category deleted"}
