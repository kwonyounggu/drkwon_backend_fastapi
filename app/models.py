# app/db/models.py
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    user_type = Column(String(20), nullable=False)
    is_banned = Column(Boolean, default=False)
    auth_method = Column(String(20), nullable=False)
    google_id = Column(String(100), unique=True)
    name = Column(String(100))
    picture = Column(String)
    refresh_token = Column(String, nullable=True)  # Add this field
    created_at = Column(TIMESTAMP, server_default=func.now())

    blogs = relationship("Blog", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    actions_taken = relationship("AdminAction", foreign_keys="AdminAction.admin_id")
    login_history = relationship("LoginHistory", back_populates="user")

class Blog(Base):
    __tablename__ = "blogs"

    blog_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    visibility = Column(String(20), nullable=False, default='Public')
    is_hidden = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    author = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog")

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogs.blog_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    blog = relationship("Blog", back_populates="comments")
    user = relationship("User", back_populates="comments")

class AdminAction(Base):
    __tablename__ = "admin_actions"

    action_id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    target_blog_id = Column(Integer, ForeignKey("blogs.blog_id", ondelete="CASCADE"))
    target_comment_id = Column(Integer, ForeignKey("comments.comment_id", ondelete="CASCADE"))
    action_type = Column(String(20), nullable=False)
    reason = Column(Text)
    action_timestamp = Column(TIMESTAMP, server_default=func.now())

class LoginHistory(Base):
    __tablename__ = "login_history"

    login_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    login_timestamp = Column(TIMESTAMP, server_default=func.now())
    ip_address = Column(String)
    user_agent = Column(Text)
    is_success = Column(Boolean, nullable=False)
    failure_reason = Column(Text)

    user = relationship("User", back_populates="login_history")

# CRUD functions and Pydantic schemas incoming next! 🚀
