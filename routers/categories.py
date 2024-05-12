import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from db import engine
from models.categories import Category, CategoryBase, CategoryCreate

category_router = APIRouter(prefix="/categories", tags=["categories"])


def get_session():
    with Session(engine) as session:
        yield session


@category_router.get("/", response_model=list[CategoryBase], status_code=200)
async def get_categories(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100):
    return session.exec(select(Category).offset(offset).limit(limit)).all()


@category_router.get("/{id}", response_model=CategoryBase, status_code=200)
async def get_category(*, session: Session = Depends(get_session), id: uuid.UUID):
    category = session.get(Category, id)
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
