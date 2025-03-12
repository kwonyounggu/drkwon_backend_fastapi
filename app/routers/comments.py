# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database


db_dependency = Depends(database.get_db)

# Comment Routes
comment_router = APIRouter(prefix="/comments", tags=["Comments"])

@comment_router.post("/", response_model=schemas.CommentResponse)
def create_comment(comment: schemas.CommentCreate, blog_id: int, user_id: int, db: Session = db_dependency):
    return crud.create_comment(db, comment, blog_id, user_id)


@comment_router.get("/blog/{blog_id}", response_model=list[schemas.CommentResponse])
def read_comments(blog_id: int, db: Session = db_dependency):
    return crud.get_comments_by_blog(db, blog_id)

#######################
# Update comments.py routes
comment_router = APIRouter(prefix="/blogs/{blog_id}/comments", tags=["Comments"])

@comment_router.post("/", response_model=schemas.CommentResponse)
def create_comment(
    blog_id: int,
    comment: schemas.CommentCreate,
    db: Session = db_dependency
):
    return crud.create_comment(db, comment, blog_id, user_id=1)  # Temp user_id - replace with auth

@comment_router.get("/", response_model=list[schemas.CommentResponse])
def read_comments(blog_id: int, db: Session = db_dependency):
    return crud.get_comments_by_blog(db, blog_id)
