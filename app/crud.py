# CRUD functions for FastAPI with SQLAlchemy

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from . import models, schemas
from passlib.context import CryptContext

#pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# User CRUD
'''
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        user_type=user.user_type,
        auth_method=user.auth_method,
        name=user.name,
        picture=user.picture
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
'''

def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_password = pwd_context.hash(user.password) if user.password else None
        
        db_user = models.User(
            email=user.email,
            password_hash=hashed_password,
            user_type=user.user_type,
            auth_method=user.auth_method,
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
    return db.query(models.User).filter(models.User.user_id == user_id).first()


def get_user_by_email(db: Session, email: str):
    #return db.query(models.User).filter(models.User.email == email).first()
    return db.query(models.User).filter(models.User.email == email).first()
    
def update_user(db: Session, user_id: int, updates: schemas.UserCreate):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user_refresh_token(db: Session, user_id: int, refresh_token: str):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if db_user:
        db_user.refresh_token = refresh_token # type: ignore
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    db.delete(db_user)
    db.commit()

# Blog CRUD
def create_blog(db: Session, blog: schemas.BlogCreate, author_id: int):
    db_blog = models.Blog(**blog.dict(), author_id=author_id)
    db.add(db_blog)
    db.commit()
    db.refresh(db_blog)
    return db_blog


def get_blog(db: Session, blog_id: int):
    return db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()


def update_blog(db: Session, blog_id: int, updates: schemas.BlogCreate):
    db_blog = db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()
    for key, value in updates.dict(exclude_unset=True).items():
        setattr(db_blog, key, value)
    db.commit()
    db.refresh(db_blog)
    return db_blog


def delete_blog(db: Session, blog_id: int):
    db_blog = db.query(models.Blog).filter(models.Blog.blog_id == blog_id).first()
    db.delete(db_blog)
    db.commit()

# Comment CRUD
def create_comment(db: Session, comment: schemas.CommentCreate, blog_id: int, user_id: int):
    db_comment = models.Comment(**comment.dict(), blog_id=blog_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments_by_blog(db: Session, blog_id: int):
    return db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()


def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.comment_id == comment_id).first()
    db.delete(db_comment)
    db.commit()

# Admin Action CRUD
def create_admin_action(db: Session, action: schemas.AdminActionRequest, admin_id: int):
    db_action = models.AdminAction(**action.dict(), admin_id=admin_id)
    db.add(db_action)
    db.commit()
    db.refresh(db_action)
    return db_action


def get_admin_actions(db: Session, admin_id: int):
    return db.query(models.AdminAction).filter(models.AdminAction.admin_id == admin_id).all()

# Login History CRUD
def log_login_attempt(db: Session, login: schemas.LoginHistoryResponse, user_id: int):
    db_login = models.LoginHistory(**login.dict(), user_id=user_id)
    db.add(db_login)
    db.commit()
    db.refresh(db_login)
    return db_login


def get_login_history(db: Session, user_id: int):
    return db.query(models.LoginHistory).filter(models.LoginHistory.user_id == user_id).all()

# 🚀 Now you’ve got fully functional CRUD functions for each model!
