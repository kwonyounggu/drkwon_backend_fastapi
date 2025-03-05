from fastapi import FastAPI, HTTPException
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from datetime import datetime, timedelta

app = FastAPI()

# Google OAuth settings
GOOGLE_CLIENT_ID = "apps.googleusercontent.com"
SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake user database
fake_db = {}

@app.post("/google-login")
async def google_login(token: str):
    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)

        # Extract user information
        email = id_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Invalid Google token")

        # Create or retrieve user account
        if email not in fake_db:
            fake_db[email] = {"email": email, "name": id_info.get("name")}

        # Issue a JWT token
        access_token = jwt.encode(
            {"sub": email, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)},
            SECRET_KEY,
            algorithm=ALGORITHM,
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")