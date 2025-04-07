# FastAPI (main.py) - Google Login (Simplified)

from datetime import timedelta
import logging
from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import RedirectResponse
import httpx  # For making HTTP requests
import os
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from urllib.parse import urlencode

from pydantic import BaseModel

from .routers.users import user_router
from .routers.blogs import blog_router
from .routers.comments import comment_router
from .routers.admin_actions import admin_router
from .routers.login_history import login_router

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import SessionLocal
from app.db import schemas, crud
from app.db.events import update_updated_at_before_update #set event listener

from fastapi.middleware.cors import CORSMiddleware

from app.utils import utils, constants

app = FastAPI()

##### The simplest way to protect access to /docs and /redoc #####
app = FastAPI(docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
             redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None)


##### you need user name and password to access: https://gemini.google.com/app/5b577630420cefaa


#This allows your Flutter app (running on localhost:3000, or whatever port you use) to call FastAPI.
app.add_middleware(
    CORSMiddleware,
    # allow_origins=[constants.FLUTTER_HOST_URL],  # Your Flutter web app URL
    allow_origins=["*"],
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

# see https://chatgpt.com/c/67e59e66-4d78-800a-8baa-35c635b6b1d7
logger = logging.getLogger(__name__)

@app.get("/login/google")
async def google_login(whereFrom: str = Query(None)):
    logger.info("===> google_login(", whereFrom, ") is called")
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
async def google_callback(request: Request, code: str = Query(None), error: str = Query(None), state: str = Query(None), db: Session = Depends(get_db)):
    logger.info("===> google_callback(", code, state, ") is called")
    if error:
        raise HTTPException(status_code=400, detail=f"Google OAuth error: {error}")
    
    if not code:
        raise HTTPException(status_code=400, detail="Authorization code is missing")
    
    # for login_history with client information
    client_info = utils.get_client_info(request)

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

            logger.info("===> user_info: ", user_info)

            # Check if user exists in the database
            user = crud.get_user_by_email(db, user_info.get("email"))
            logger.info("user returned from table: ", user)
            
            #Just insert a new record if not existing in table
            if not user:
                # Add the user if not found
                new_user = schemas.UserCreate(
                    email=user_info.get("email"),
                    password="",
                    user_type="general", # general, od, md, admin
                    auth_method="google",
                    google_id=user_info.get("sub"),
                    name=user_info.get("name"),
                    picture=user_info.get("picture")
                )
                user = crud.create_user(db, new_user)
                logger.info("===> created user:", user)

            client_info['user_id'] = user.user_id # type: ignore

            access_token = utils.create_access_token(
            {     
                "user_id": user.user_id, # type: ignore               
                "email": user.email, # type: ignore
                "user_type": user.user_type,  # type: ignore
                "auth_method":user.auth_method,  # type: ignore
                "is_banned":user.is_banned, # type: ignore
                "name": user.name, # type: ignore
                "picture": user.picture # type: ignore
            })
            
            #print("New user object:", new_user.dict())
            refresh_token = utils.create_refresh_token(user.user_id, user.email) # type: ignore

            # Store the refresh token in the database (optional but safer)
            user = crud.update_user_refresh_token(db, user.user_id, refresh_token) # type: ignore
            
            #login history
            crud.create_login_history(db, client_info)

            redirect_url = f"{constants.FLUTTER_HOST_URL}/#/login?jwt={access_token}&refresh={refresh_token}"
            if state:  # If 'from' parameter exists, append it to the redirect URL
                redirect_url += f"&whereFrom={state}&doit=1"

            return RedirectResponse(url=redirect_url)
    except httpx.HTTPStatusError as e:
        logger.error(f"httpx.HTTPStatusError: {e}") # full stack trace then add logger.error(f"..", exc_info=True).
        raise HTTPException(status_code=e.response.status_code, detail="Failed to communicate with Google OAuth")
    except SQLAlchemyError as e:
        db.rollback() # safe in SQLALchemy
        logger.error(f"SQLAlchemyError: {e}")
        raise HTTPException(status_code=500, detail="Database error")
    except Exception as e:
        logger.error(f"Exception: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
        
     
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
@app.post("/refresh")
async def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        refresh_token = request.refresh_token
        print("--- 0 ---", refresh_token)

        payload = jwt.decode(refresh_token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM]) # type: ignore
        print("--- 0.1 ---", payload)
        user_id = payload.get("sub")
        print("--- 0.2 ---", user_id)
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token no user_id")
        print("--- 1 ---")
        # Verify the refresh token is valid and matches the one in the database
        user = crud.get_user_by_id(db, int(user_id))
        if not user or user.refresh_token != refresh_token: # type: ignore
            #print("user: ", user, " user.refresh_token=", user.refresh_token) # type: ignore
            raise HTTPException(status_code=401, detail="Invalid refresh token, no user object or different refresh_token")
        print("--- 2 ---")
        # Generate a new access token
        new_access_token = utils.create_access_token(
            {
                "user_id": user.user_id, 
                "email": user.email,
                "user_type": user.user_type, 
                "auth_method":user.auth_method, 
                "is_banned":user.is_banned,
                "picture": user.picture
            })
        print("--- 3 ---")
        return {"access_token": new_access_token}

    except ExpiredSignatureError as e:
        logger.error(f"ExpiredSignatureError: {e}")
        raise HTTPException(status_code=401, detail="Refresh token has expired")
    except JWTError as e:
        logger.error(f"JWTError: {e}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
