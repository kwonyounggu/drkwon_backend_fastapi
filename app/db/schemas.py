from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: str
    auth_method: str
    google_id: Optional[str]
    name: Optional[str]
    picture: Optional[str]

class UserUpdateRefreshToken(BaseModel):
    refresh_token: Optional[str]

class UserRoleUpdate(BaseModel):
    new_role: str  #general, od, md, admin
    
class UserResponse(BaseModel):
    user_id: int
    email: str
    user_type: str
    name: Optional[str]
    picture: Optional[str]
    refresh_token: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class BlogCreate(BaseModel):
    title: str
    content: str
    visibility: str

class BlogListResponse(BaseModel):
    blog_id: int
    title: str
    #content: str
    rating: float
    num_views: int
    #visibility: str
    #is_hidden: bool
    updated_at: datetime
    #created_at: datetime
    cover_image: str
    #allow_comments: bool
    excerpt: str
    estimated_reading_time: int
    #meta_title: str
    #meta_description: str
    #keywords: str
    slug: str #10-tips-for-eye-health-in-2025 from 10 Tips for Eye Health in 2025
    author: UserResponse

    class Config:
        from_attributes = True

class BlogSpecificResponse(BaseModel):
    blog_id: int
    title: str
    content: str
    rating: float
    num_views: int
    visibility: str
    is_hidden: bool
    updated_at: datetime
    created_at: datetime
    cover_image: str
    allow_comments: bool
    estimated_reading_time: int
    meta_title: str
    meta_description: str
    keywords: str
    slug: str #A slug is a URL-friendly version of a blog title, typically lowercase, with spaces and special characters replaced by dashes.
    author: UserResponse

    class Config:
        from_attributes = True

class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    comment_id: int
    content: str
    is_hidden: bool
    created_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True

#For creating an action (e.g., banning a user or hiding content).
class AdminActionRequest(BaseModel):
    target_user_id: Optional[int] = None
    target_blog_id: Optional[int] = None
    target_comment_id: Optional[int] = None
    action_type: str #'BanUser', 'HideBlog', 'HideComment'
    reason: str #Reason for the action

#For returning the action details
class AdminActionResponse(AdminActionRequest):
    action_id: int
    action_type: str
    action_timestamp: datetime

    class Config:
        from_attributes = True

class LoginHistoryResponse(BaseModel):
    login_id: int
    login_timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    is_success: bool
    failure_reason: Optional[str]

    class Config:
        from_attributes = True
