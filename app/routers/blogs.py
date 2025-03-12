# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.security import get_current_user
from .. import crud, schemas, database, models


db_dependency = Depends(database.get_db)

# Blog Routes
blog_router = APIRouter(prefix="/blogs", tags=["Blogs"])

#@blog_router.post("/", response_model=schemas.BlogResponse)
#def create_blog(blog: schemas.BlogCreate, author_id: int, db: Session = db_dependency): # type: ignore
#    return crud.create_blog(db, blog, author_id)


@blog_router.get("/{blog_id}", response_model=schemas.BlogResponse)
def read_blog(blog_id: int, db: Session = db_dependency):
    db_blog = crud.get_blog(db, blog_id)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found")
    return db_blog

#############
@blog_router.get("/", response_model=list[schemas.BlogResponse])
def read_blogs(
    visibility: str = Query(None, description="Filter by visibility (Public/Doctors)"),
    db: Session = db_dependency
):
    query = db.query(models.Blog)
    if visibility:
        query = query.filter(models.Blog.visibility == visibility)
    return query.all()

# Add patch and delete endpoints
@blog_router.patch("/{blog_id}", response_model=schemas.BlogResponse)
def update_blog(
    blog_id: int,
    blog_update: schemas.BlogCreate,
    db: Session = db_dependency
):
    return crud.update_blog(db, blog_id, blog_update)

@blog_router.delete("/{blog_id}")
def delete_blog_endpoint(blog_id: int, db: Session = db_dependency):
    crud.delete_blog(db, blog_id)
    return {"message": "Blog deleted successfully"}

# Example protected endpoint
@blog_router.post("/", response_model=schemas.BlogResponse)
def create_blog(
    blog: schemas.BlogCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = db_dependency
):
    if current_user.user_type not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.create_blog(db, blog, current_user.user_id)

