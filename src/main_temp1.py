from fastapi import Depends, HTTPException, status, Header, FastAPI
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import jwt
from datetime import datetime, timedelta, timezone

import os

# ... (other imports, SECRET_KEY, ALGORITHM, database setup)

CLIENT_ID = "1037051096786-g3657uojp3s60vbstbef6u87k1ja11qt.apps.googleusercontent.com" #Replace with your client ID.
ACCESS_TOKEN_EXPIRE_MINUTES = 30 # example.

jwt_secret_key = os.environ.get("JWT_SECRET_KEY")
if jwt_secret_key is None:
    print("Error: SECRET_KEY is not retrieved")

SECRET_KEY = jwt_secret_key if jwt_secret_key is not None else "webmonster.ca" #example, store in env vars.
ALGORITHM = "HS256"

app = FastAPI() # Define the FastAPI app instance

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    now = datetime.now(timezone.utc) # Corrected line.
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/test")
async def test_endpoint():
    token = create_access_token({"sub": "testuser"})
    return {"token": token}

@app.post("/google_login")
async def google_login(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header missing")

    try:
        idinfo = id_token.verify_oauth2_token(authorization.split('Bearer ')[1], requests.Request(), CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise HTTPException(status_code=400, detail="Wrong issuer.")

        userid = idinfo['sub']
        email = idinfo['email']
        #check if user exists in database, if not create them.
        #user = get_user(email=email) #replace with db call.
        user = {"email": email} #replace with DB call.
        if not user:
            #Create user in database.
            pass

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))