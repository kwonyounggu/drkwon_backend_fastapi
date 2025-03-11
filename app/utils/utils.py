# see for more info from https://www.perplexity.ai/search/in-fastapi-python-encoded-jwt-FxGI_2uNRyqluZYPQCMTpw
from jose import jwt
from datetime import datetime, timedelta, timezone
#import secrets
from app.utils import constants

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
    
    to_encode.update({
        #"sub": user_info_from_google["sub"],
        #"name": user_info_from_google["name"],
        #"picture_url": user_info_from_google["picture"],
        #"email": user_info_from_google["email"],
        "exp": expire,
        "iat": now,
        "iss": constants.APP_NAME
    })
    
    to_encode.update(user_info_from_db)
    
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: int, expires_delta: timedelta = None):
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)  # Long-lived refresh token

    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM) 
    return encoded_jwt

# Example usage
#user_id = '100402364199988459535'
#additional_info = {'name': 'younggu kwon', 'email': 'webmonster.ca@gmail.com'}
#jwt_token = create_access_token(user_id, additional_info)

#Important: To get all the information you need scope of openid email profile.
"""
{
 'sub': '<unique_id>',
 'name': '<full>',
 'given_name': '<first>',
 'family_name': '<last>',
 'picture': '<pic>',
 'email': '<email>',
 'email_verified': True,
 'locale': 'en'
}
"""

'''
def create_access_token(user_id: str, additional_claims: dict = None, expires_delta: timedelta = None):
    to_encode = {}
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=constants.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "iss": constants.APP_NAME
    })
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, constants.SECRET_KEY, algorithm=constants.ALGORITHM)
    return encoded_jwt

from datetime import datetime, timedelta
import jwt
from app.config import settings

def create_access_token(user_id: str, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)  # Short-lived access token
    to_encode.update({"exp": expire, "sub": user_id})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(user_id: str, expires_delta: timedelta = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)  # Long-lived refresh token
    to_encode = {"exp": expire, "sub": user_id}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
'''