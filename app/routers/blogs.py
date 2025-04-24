# API Routes for FastAPI with SQLAlchemy

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.security import get_current_user
from app.db import crud, schemas, database, models


db_dependency = Depends(database.get_db)

# Blog Routes
blog_router = APIRouter(prefix="/blogs", tags=["Blogs"])

#@blog_router.post("/", response_model=schemas.BlogResponse)
#def create_blog(blog: schemas.BlogCreate, author_id: int, db: Session = db_dependency): # type: ignore
#    return crud.create_blog(db, blog, author_id)

# See https://grok.com/chat/4ba28422-595c-4b11-be92-e9633ca631d3
# Like or dislike a blog
@blog_router.post("/{blog_id}/reaction", response_model=schemas.BlogReactionResponse)
def react_to_blog(
    blog_id: int,
    reaction: schemas.BlogReactionCreate,
    db: Session = db_dependency,
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    
    if reaction.reaction_type not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid reaction type")
    return crud.create_or_update_reaction(db, blog_id, current_user.user_id, reaction)

# Get user's reaction for a blog
@blog_router.get("/{blog_id}/my-reaction", response_model=Optional[schemas.BlogReactionResponse])
def get_my_reaction(
    blog_id: int,
    db: Session = db_dependency,
    current_user: schemas.UserResponse = Depends(get_current_user)
):
    
    reaction = crud.get_user_reaction(db, blog_id, current_user.user_id)
    return reaction

@blog_router.get("/{blog_id}", response_model=schemas.BlogSpecificResponse)
def read_blog(
    blog_id: int, 
    db: Session = db_dependency,
    current_user: schemas.UserResponse = Depends(get_current_user, use_cache=False)):

    db_blog = crud.get_blog(db, blog_id)
    if db_blog is None:
        raise HTTPException(status_code=404, detail="Blog not found with ${blog_id}")
    
    # Add user's reaction
    reaction = crud.get_user_reaction(db, blog_id, current_user.user_id)
    db_blog.user_reaction = reaction.reaction_type if reaction else None
    
    return db_blog

#############
# See https://chatgpt.com/c/67ef277f-3ff8-800a-95e3-c1e90d14fd96, problem is sorting
# fixed from https://grok.com/chat/c7c3ed2c-9cbd-4da8-b253-912ca626564c
@blog_router.get("/", response_model=list[schemas.BlogListResponse])
def read_blogs(
    visibility: Optional[str] = Query(None, description="Filter by visibility (public/doctor)"),
    is_hidden: Optional[bool] = Query(None, description="Filter by hidden status (True/False)"),
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    per_page: int = Query(10, ge=1, le=100, description="Number of records per page"),
    db: Session = db_dependency
):
    
    query = db.query(models.Blog)
    if visibility and visibility in ['public', 'doctor']:
        query = query.filter(models.Blog.visibility == visibility.lower())
    if is_hidden is not None:
        query = query.filter(models.Blog.is_hidden == is_hidden)

    # Soft delete filter (optional but recommended)
    query = query.filter(models.Blog.deleted_at == None)

    # Order by most recent
    query = query.order_by(desc(models.Blog.updated_at), desc(models.Blog.blog_id))
    
    # Pagination
    offset = (page - 1) * per_page
    blogs = query.offset(offset).limit(per_page).all()

    #print(f"Page {page}, Per_page {per_page}: {[blog.title for blog in blogs]}")
    
    return blogs

# Add patch and delete endpoints
@blog_router.patch("/{blog_id}", response_model=schemas.BlogSpecificResponse)
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
# see https://gemini.google.com/gem/coding-partner/d6794c28c9739883
# will show you how to create keywords, summary/excerpt
@blog_router.post("/", response_model=schemas.BlogSpecificResponse)
def create_blog(
    blog: schemas.BlogCreate,
    current_user: schemas.UserResponse = Depends(get_current_user),
    db: Session = db_dependency
):
    if current_user.user_type not in ["doctor", "admin"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return crud.create_blog(db, blog, current_user.user_id)

