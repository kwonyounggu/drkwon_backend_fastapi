# CRUD functions for FastAPI with SQLAlchemy

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas
from passlib.context import CryptContext

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password) if user.password else None
        
        db_user = models.User(
            email=user.email,
            password_hash=hashed_password,
            user_type=user.user_type,
            auth_method=user.auth_method,
            google_id=user.google_id,
            name=user.name,
            picture=user.picture
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except SQLAlchemyError as e:
        db.rollback()
        print(f"SQLAlchemyError during user creation: {e}")
        return None


def get_user_by_id(db: Session, user_id: int):
    try:
        return db.query(models.User).filter(models.User.user_id == user_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

def get_user_by_email(db: Session, email: str):
    try:
        return db.query(models.User).filter(models.User.email == email).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

    
def update_user(db: Session, user_id: int, updates: schemas.UserCreate):
    try:
        db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        for key, value in updates.dict(exclude_unset=True).items():
            setattr(db_user, key, value)

        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update user")

def update_user_refresh_token(db: Session, user_id: int, refresh_token: str):
    try:
        db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.refresh_token = refresh_token  # type: ignore
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update refresh token")

def update_user_role(db: Session, user_id: int, new_role: str):
    try:
        db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Optional: Validate `new_role` against allowed values
        allowed_roles = {"General", "Doctor", "Admin"}
        if new_role not in allowed_roles:
            raise HTTPException(status_code=400, detail="Invalid role")

        db_user.user_type = new_role # type: ignore
        db.commit()
        db.refresh(db_user)  # Ensure the session reflects the updated object
        return db_user

    except SQLAlchemyError as e:
        db.rollback()  # Rollback on error
        print(f"SQLAlchemyError during update_user_role: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
        #raise HTTPException(status_code=500, detail="Failed to update role, please try again")


def delete_user(db: Session, user_id: int):
    try:
        db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db.delete(db_user)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Blog CRUD
def create_blog(db: Session, blog: schemas.BlogCreate, author_id: int):
    try:
        db_blog = models.Blog(**blog.dict(), author_id=author_id)
        db.add(db_blog)
        db.commit()
        db.refresh(db_blog)
        return db_blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create blog")


def get_blog(db: Session, blog_id: int):
    try:
        return db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    
'''
modify later
# Update get_blog function in crud.py
def get_blog(db: Session, blog_id: int):
    return db.query(models.Blog).options(
        joinedload(models.Blog.author),
        joinedload(models.Blog.comments).joinedload(models.Comment.user)
    ).filter(models.Blog.blog_id == blog_id).first()

'''

def update_blog(db: Session, blog_id: int, updates: schemas.BlogCreate):
    try:
        db_blog = db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()
        if not db_blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        for key, value in updates.dict(exclude_unset=True).items():
            setattr(db_blog, key, value)

        db.commit()
        db.refresh(db_blog)
        return db_blog
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update blog")


def delete_blog(db: Session, blog_id: int):
    try:
        db_blog = db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()
        if not db_blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        db.delete(db_blog)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete blog")

# Comment CRUD
def create_comment(db: Session, comment: schemas.CommentCreate, blog_id: int, user_id: int):
    try:
        db_comment = models.Comment(**comment.dict(), blog_id=blog_id, user_id=user_id)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create comment")

def get_comments_by_blog(db: Session, blog_id: int):
    try:
        return db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

def delete_comment(db: Session, comment_id: int):
    try:
        db_comment = db.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()
        if not db_comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        db.delete(db_comment)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete comment")

# Admin Action CRUD
def create_admin_action(db: Session, action: schemas.AdminActionRequest, admin_id: int):
    try:
        db_action = models.AdminAction(**action.dict(), admin_id=admin_id)
        db.add(db_action)
        db.commit()
        db.refresh(db_action)
        return db_action
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create admin action")


def get_admin_actions(db: Session, admin_id: int):
    try:
        return db.query(models.AdminAction).filter(models.AdminAction.admin_id == admin_id).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")

# Login History CRUD
def log_login_attempt(db: Session, login: schemas.LoginHistoryResponse, user_id: int):
    try:
        db_login = models.LoginHistory(**login.dict(), user_id=user_id)
        db.add(db_login)
        db.commit()
        db.refresh(db_login)
        return db_login
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to log login attempt")
    
def create_login_history(db: Session, client_info:dict):
    try:
        db_login_history = models.LoginHistory(
            user_id=client_info['user_id'],
            ip_address=client_info['client_ip'],
            user_agent=client_info['user_agent'],
            is_success=True,
            device_id=client_info['device'],
            location=client_info['location'],
            os=client_info['os'],
            browser=client_info['browser']
        )
        db.add(db_login_history)
        db.commit()
        db.refresh(db_login_history)
        return db_login_history
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to insert a login_history record: ${e}")

def get_login_history(db: Session, user_id: int):
    try:
        return db.query(models.LoginHistory).filter(models.LoginHistory.user_id == user_id).all()
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")
    
# 🚀 Now you’ve got fully functional CRUD functions for each model!
