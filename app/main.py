# FastAPI (main.py) - Google Login (Simplified)

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import RedirectResponse
import httpx  # For making HTTP requests

from urllib.parse import urlencode

from .routers.users import user_router
from .routers.blogs import blog_router
from .routers.comments import comment_router
from .routers.admin_actions import admin_router
from .routers.login_history import login_router

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

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
                                    "client_id": constants.GOOGLE_CLIENT_ID,
                                    "redirect_uri": constants.GOOGLE_REDIRECT_URI,
                                    "response_type": "code",
                                    "scope": "openid email profile",
                               }
    
    if whereFrom:
        params["state"] = whereFrom  # Pass whereFrom as a separate parameter
    auth_url = f"{constants.GOOGLE_AUTH_URL}?{urlencode(params)}"

    return RedirectResponse(auth_url)

@app.get("/login/google/callback")
async def google_callback(code: str = Query(None), error: str = Query(None), state: str = Query(None), db: Session = Depends(get_db)):
    print("===> google_callback(", code, state, ") is called")
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")

    token_data = {
                                    "client_id": constants.GOOGLE_CLIENT_ID,
                                    "client_secret": constants.GOOGLE_CLIENT_SECRET,
                                    "code": code,
                                    "grant_type": "authorization_code",
                                    "redirect_uri": constants.GOOGLE_REDIRECT_URI,
                                 }
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(constants.GOOGLE_TOKEN_URL, data=token_data)
            token_response.raise_for_status()
            tokens = token_response.json()

            user_info_response = await client.get(constants.GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {tokens['access_token']}"},)
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

            #jwt_token = utils.create_access_token(user_info["sub"], {"name": user_info["name"], "email": user_info["email"]})
            jwt_token = utils.create_access_token(user_info, {"user_id": user.user_id, "user_type": user.user_type, "auth_method":user.auth_method, "is_banned":user.is_banned})
            #return {"token": jwt_token} #For simplicity, we return the token directly.
            # Redirect back to your Flutter app with the token
            print("=> callback from ", state)
            redirect_url = f"{constants.FLUTTER_HOST_URL}/#/login?jwt={jwt_token}"
            if state:  # If 'from' parameter exists, append it to the redirect URL
                redirect_url += f"&whereFrom={state}&doit=1"
            return RedirectResponse(url=redirect_url)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Failed to communicate with Google OAuth")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    
'''
@app.post("/refresh")
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Verify the refresh token is valid and matches the one in the database
        user = crud.get_user_by_id(db, user_id)
        if not user or user.refresh_token != refresh_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # Generate a new access token
        new_access_token = utils.create_access_token(user_id, {"email": user.email}, expires_delta=timedelta(minutes=15))
        return {"access_token": new_access_token}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
'''