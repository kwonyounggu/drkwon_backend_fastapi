# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database


db_dependency = Depends(database.get_db)

# Blog Routes
blog_router = APIRouter(prefix="/blogs", tags=["Blogs"])

@blog_router.post("/", response_model=schemas.BlogResponse)
def create_blog(blog: schemas.BlogCreate, author_id: int, db: Session = db_dependency):
    return crud.create_blog(db, blog, author_id)


@blog_router.get("/{blog_id}", response_model=schemas.BlogResponse)
def read_blog(blog_id: int, db: Session = db_dependency):
    db_blog = crud.get_blog(db, blog_id)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog