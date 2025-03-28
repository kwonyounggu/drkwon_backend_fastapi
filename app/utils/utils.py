# see for more info from https://www.perplexity.ai/search/in-fastapi-python-encoded-jwt-FxGI_2uNRyqluZYPQCMTpw
import json
from fastapi import Request
from jose import jwt
from datetime import datetime, timedelta, timezone
#import secrets
from app.utils import constants

import requests
from user_agents import parse

'''
SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
'''

#def create_access_token(user_info_from_google: dict, user_info_from_db: dict, expires_delta: timedelta = None):
def create_access_token(user_info_from_db: dict, expires_delta: timedelta = None):
    to_encode = {}
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update(
    {
        "exp": expire,
        "iat": now,
        "iss": constants.APP_NAME
    })
    
    to_encode.update(user_info_from_db)
    
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM) # type: ignore
    return encoded_jwt

def create_refresh_token(user_id: int, email: str, expires_delta: timedelta = None):
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)  # Long-lived refresh token

    to_encode = {"exp": expire, "sub": str(user_id), "email": email, "iat": now, "iss": constants.APP_NAME}
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)  # type: ignore
    return encoded_jwt


def get_client_info(request: Request):
    # Extract client IP address
    client_ip = request.client.host # type: ignore

    # Extract user agent
    user_agent = request.headers.get("user-agent", "Unknown")

    # Parse user agent details
    parsed_ua = parse(user_agent)
    device = parsed_ua.device.family or "Unknown"
    browser = parsed_ua.browser.family or "Unknown"
    os = parsed_ua.os.family or "Unknown"

    # Get approximate geolocation (optional)
    try:
        geo_info = requests.get(f"https://ipinfo.io/{client_ip}/json", timeout=3).json()
        location = {
            "city": geo_info.get("city", "Unknown"),
            "region": geo_info.get("region", "Unknown"),
            "country": geo_info.get("country", "Unknown"),
        }
    except requests.RequestException:
        location = {"city": "Unknown", "region": "Unknown", "country": "Unknown"}

    # Return all info in a dictionary
    return {
        "client_ip": client_ip,
        "user_agent": user_agent,
        "device": device,
        "browser": browser,
        "os": os,
        "location": json.dumps(location), # json.loads(entry.location) to convert it back
    }
