import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from auth.login import manager
from db import engine
from models.articles import Article, ArticleBase, ArticleCreate

article_router = APIRouter(prefix="/articles", tags=["articles"])


def get_session():
    with Session(engine) as session:
        yield session


@article_router.get("/", response_model=list[ArticleBase], status_code=200)
async def get_articles(*, session: Session = Depends(get_session), offset: int = 0, limit: int = 100, student: str = None):
    articles = session.exec(
        select(Article).join(Article.category).offset(offset).limit(limit).where(Article.student == student)
    ).all()

    articles_base = []
    for article in articles:
        article_base = ArticleBase(
            id=article.id,
            name=article.name,
            units=article.units,
            image=article.image,
            description=article.description,
            purchase_price=article.purchase_price,
            sale_price=article.sale_price,
            created_at=article.created_at,
            updated_at=article.updated_at,
            deleted_at=article.deleted_at,
            category=article.category.dict() if article.category else None,
            student=article.student,
        )
        articles_base.append(article_base)

    return articles_base


@article_router.get("/{id}", response_model=ArticleBase, status_code=200)
async def get_article(*, session: Session = Depends(get_session), id: uuid.UUID):
    article = session.get(Article, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    article_base = ArticleBase(
        id=article.id,
        name=article.name,
        units=article.units,
        image=article.image,
        description=article.description,
        purchase_price=article.purchase_price,
        sale_price=article.sale_price,
        created_at=article.created_at,
        updated_at=article.updated_at,
        deleted_at=article.deleted_at,
        category=article.category.dict() if article.category else None,
        student=article.student,
    )

    return article_base


@article_router.post("/", response_model=ArticleBase, status_code=201)
async def create_article(*, session: Session = Depends(get_session), article: ArticleCreate):
    db_article = Article(**article.dict())
    session.add(db_article)
    session.commit()
    session.refresh(db_article)

    article_base = ArticleBase(
        id=db_article.id,
        name=db_article.name,
        image=db_article.image,
        description=db_article.description,
        units=db_article.units,
        purchase_price=db_article.purchase_price,
        sale_price=db_article.sale_price,
        created_at=db_article.created_at,
        updated_at=db_article.updated_at,
        deleted_at=db_article.deleted_at,
        category=db_article.category.dict() if db_article.category else None,
        student=db_article.student,
    )

    return article_base


@article_router.patch("/{id}", response_model=ArticleBase, status_code=200)
async def update_article(*, session: Session = Depends(get_session), id: uuid.UUID, article: ArticleCreate):
    db_article = session.get(Article, id)
    if not db_article:
        raise HTTPException(status_code=404, detail="Article not found")
    article_data = article.model_dump(exclude_unset=True)
    for key, value in article_data.items():
        setattr(db_article, key, value)
    session.add(db_article)
    session.commit()
    session.refresh(db_article)
    return db_article


@article_router.delete("/{id}")
def delete_article(*, session: Session = Depends(get_session), id: uuid.UUID):
    article = session.get(Article, id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    session.delete(article)
    session.commit()
    return {"message": "Article deleted"}
