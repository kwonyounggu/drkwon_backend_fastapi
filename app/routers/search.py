from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import schemas, database
from app.db.models import Blog, User, Comment


db_dependency = Depends(database.get_db)

search_router = APIRouter(prefix="/search", tags=["Search"])

@search_router.get("/", response_model=list[schemas.SearchResult])
def search(query: str = Query(..., min_length=1), include_author: bool = Query(False), db: Session = db_dependency):

    search_query = f"%{query}%"
    # Simplified search example
    blog_query = db.query(Blog).join(User).filter(
        (Blog.title.ilike(search_query)) |
        (Blog.content.ilike(search_query)) |
        (User.name.ilike(search_query) if include_author else False)
    )

    comment_query = db.query(Comment).join(User).filter(
        (Comment.content.ilike(search_query)) |
        (User.name.ilike(search_query) if include_author else False)
    )

    blogs = blog_query.all()
    comments = comment_query.all()

    results = []
    for blog in blogs:
        results.append(schemas.SearchResult(
            type="blog",
            id=blog.blog_id, # type: ignore
            title=blog.title, # type: ignore
            content=blog.excerpt, # type: ignore because content is too long
            author_name=blog.author.name if blog.author else "Unknown",
            likes=blog.likes, # type: ignore
            dislikes=blog.dislikes, # type: ignore
            date=blog.updated_at # type: ignore
        ))

    for comment in comments:
        results.append(schemas.SearchResult(
            type="comment",
            id=comment.blog_id, # type: ignore
            content=comment.content, # type: ignore
            author_name=comment.user.name if comment.user else "Unknown",
            likes=comment.likes, # type: ignore
            dislikes=comment.dislikes, # type: ignore
            date=comment.created_at # type: ignore
        ))

    return results