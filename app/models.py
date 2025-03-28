# app/db/models.py
from sqlalchemy import JSON, Column, Integer, String, Float, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
#Gemini helped for the additional fields Mar 22 2025
#Ref: https://gemini.google.com/app/3e634dc60d18d4bf
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255))
    user_type = Column(String(20), nullable=False) # general, od, md, admin
    is_banned = Column(Boolean, default=False)
    why_is_banned = Column(Text, default=None)
    auth_method = Column(String(20), nullable=False) # traditional or google
    google_id = Column(String(100), unique=True, nullable=True)  # from google user info
    name = Column(String(100)) # google name first + last name
    picture = Column(String) # google picture link
    refresh_token = Column(String, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    phone_number = Column(String(20), nullable=True) # from profile clinic
    address = Column(Text, nullable=True) # from profile clinic
    date_of_birth = Column(TIMESTAMP, nullable=True) # from profile
    last_login = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now()) # whenever logged in
    profile_picture = Column(String, nullable=True) # from profile
    bio = Column(Text, nullable=True) # from profile, A short user description
    social_media_links = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    verification_status = Column(String(20), nullable=True, default='pending') # pending, when admin checks and approves
    language = Column(String(10), nullable=True) # profile, user's preferred language
    timezone = Column(String(50), nullable=True) # user's time zone
    location = Column(String, nullable=True) # profile, location of user
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete

    blogs = relationship("Blog", back_populates="author")
    comments = relationship("Comment", back_populates="user")
    actions_taken = relationship("AdminAction", foreign_keys="AdminAction.admin_id")
    login_history = relationship("LoginHistory", back_populates="user")

class Blog(Base):
    __tablename__ = "blogs"

    blog_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    rating = Column(Float, default=0.0)
    num_views = Column(Integer, default=0)
    author_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    visibility = Column(String(20), nullable=False, default='public')
    is_hidden = Column(Boolean, default=False)
    why_is_hidden = Column(Text, default=None)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_at = Column(TIMESTAMP, server_default=func.now())
    tags = Column(JSON, nullable=True)
    cover_image = Column(String, nullable=True)
    excerpt = Column(Text, nullable=True)
    estimated_reading_time = Column(Integer, nullable=True)
    scheduled_publication_date = Column(TIMESTAMP, nullable=True)
    category = Column(String, nullable=True)
    meta_title = Column(String, nullable=True)
    meta_description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    slug = Column(String, nullable=True)
    allow_comments = Column(Boolean, default=True)
    original_source = Column(String, nullable=True)
    language = Column(String, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete

    author = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog")

class Comment(Base):
    __tablename__ = "comments"

    comment_id = Column(Integer, primary_key=True, index=True)
    blog_id = Column(Integer, ForeignKey("blogs.blog_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_hidden = Column(Boolean, default=False)
    why_is_hidden = Column(Text, default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())
    parent_comment_id = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    edited_at = Column(TIMESTAMP, nullable=True)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    report_count = Column(Integer, default=0)
    deleted_at = Column(TIMESTAMP, nullable=True)  # Soft delete

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
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    action_details = Column(JSON, nullable=True)
    affected_resource_type = Column(String, nullable=True)
    previous_state = Column(JSON, nullable=True)

class LoginHistory(Base):
    __tablename__ = "login_history"

    login_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"))
    login_timestamp = Column(TIMESTAMP, server_default=func.now())
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    is_success = Column(Boolean, nullable=False)
    failure_reason = Column(Text, nullable=True)
    device_id = Column(String, nullable=True)
    location = Column(String, nullable=True)
    two_factor_auth_used = Column(Boolean, default=False)
    os = Column(String, nullable=True)
    browser = Column(String, nullable=True)

    user = relationship("User", back_populates="login_history")
