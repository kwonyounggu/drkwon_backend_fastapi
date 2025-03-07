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

from fastapi.middleware.cors import CORSMiddleware

from app.utils import utils, constants

app = FastAPI()

#This allows your Flutter app (running on localhost:3000, or whatever port you use) to call FastAPI.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[constants.FLUTTER_HOST_URL],  # Your Flutter web app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/login/google")
async def google_login(whereFrom: str = Query(None)):
    print("===> google_login(", whereFrom, ") is called")
    params =  {
                                    "client_id": GOOGLE_CLIENT_ID,
                                    "redirect_uri": GOOGLE_REDIRECT_URI,
                                    "response_type": "code",
                                    "scope": "openid email profile",
                               }
    
    if whereFrom:
        params["state"] = whereFrom  # Pass whereFrom as a separate parameter
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

    return RedirectResponse(auth_url)

@app.get("/login/google/callback")
async def google_callback(code: str = Query(None), error: str = Query(None), state: str = Query(None), db: Session = Depends(get_db)):
    print("===> google_callback(", code, state, ") is called")
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
        print("user returned from table: ", user)
        
        #Just insert a new record if not existing in table
        if user is None:
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
            print("===> created user:", user)

        jwt_token = utils.create_access_token(user_info["sub"], {"name": user_info["name"], "email": user_info["email"]})

        #return {"token": jwt_token} #For simplicity, we return the token directly.
        # Redirect back to your Flutter app with the token
        print("=> callback from ", state)
        redirect_url = f"{constants.FLUTTER_HOST_URL}/#/login?jwt={jwt_token}"
        if state:  # If 'from' parameter exists, append it to the redirect URL
            redirect_url += f"&whereFrom={state}"
        return RedirectResponse(url=redirect_url)