from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    user_type: str
    auth_method: str
    name: Optional[str]
    picture: Optional[str]

class UserResponse(BaseModel):
    user_id: int
    email: str
    user_type: str
    name: Optional[str]
    picture: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class BlogCreate(BaseModel):
    title: str
    content: str
    visibility: str

class BlogResponse(BaseModel):
    blog_id: int
    title: str
    content: str
    visibility: str
    is_hidden: bool
    created_at: datetime
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
    action_type: str
    reason: Optional[str] = None

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
