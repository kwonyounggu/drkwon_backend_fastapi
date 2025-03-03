# FastAPI (main.py) - Google Login (Simplified)

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import httpx  # For making HTTP requests
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
from .routers.users import user_router
from .routers.blogs import blog_router
from .routers.comments import comment_router
from .routers.admin_actions import admin_router
from .routers.login_history import login_router

from sqlalchemy.orm import Session
from app.database import SessionLocal
import app.crud as crud
import app.schemas as schemas

app = FastAPI()

# Register routers
app.include_router(user_router)
app.include_router(blog_router)
app.include_router(comment_router)
app.include_router(admin_router)
app.include_router(login_router)

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI") #e.g. "http://localhost:8000/login/google/callback"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

class User(BaseModel):
    email: str
    # ... other user fields

# In a real app, you'd store users in a database
users = {}

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_jwt(user: User):
    # In a real app, implement JWT generation here
    # (using python-jose or similar)
    print("===> generate_jwt(user: ", user, ")")
    return f"fake_jwt_for_{user.email}"

@app.get("/login/google")
async def google_login():
    print("===> google_login() is called")
    params =  {
                                    "client_id": GOOGLE_CLIENT_ID,
                                    "redirect_uri": GOOGLE_REDIRECT_URI,
                                    "response_type": "code",
                                    "scope": "openid email profile",
                               }
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(auth_url)

@app.get("/login/google/callback")
async def google_callback(code: str = Query(None), error: str = Query(None), db: Session = Depends(get_db)):
    print("===> google_callback(...) is called")
    if error:
        raise HTTPException(status_code=400, detail=error)

    token_data = {
                                    "client_id": GOOGLE_CLIENT_ID,
                                    "client_secret": GOOGLE_CLIENT_SECRET,
                                    "code": code,
                                    "grant_type": "authorization_code",
                                    "redirect_uri": GOOGLE_REDIRECT_URI,
                                 }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        tokens = token_response.json()

        user_info_response = await client.get(
                                                            GOOGLE_USERINFO_URL,
                                                            headers={"Authorization": f"Bearer {tokens['access_token']}"},
                                                        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()

        email = user_info["email"]
        name = user_info.get("name")
        picture = user_info.get("picture")
        print("===> user_info: ", user_info)

        # Check if user exists in the database
        user = crud.get_user_by_email(db, email)

        if not user:
            # Add the user if not found
            new_user = schemas.UserCreate(
                email=email,
                password="",
                user_type="General",
                auth_method="Google",
                name=name,
                picture=picture
            )
        user = crud.create_user(db, new_user)

        # Check if user exists (in a real app, check your database)
        #if email not in users:
        #    users[email] = User(email=email)  # Create a new user

        #user = users[email]
        jwt_token = generate_jwt(user)

        # In a real app, you might redirect to your frontend with the JWT
        # or return it in a JSON response.
        return {"token": jwt_token} #For simplicity, we return the token directly.