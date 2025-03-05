# see for more info from https://www.perplexity.ai/search/in-fastapi-python-encoded-jwt-FxGI_2uNRyqluZYPQCMTpw
from jose import jwt
from datetime import datetime, timedelta, timezone
import secrets
from app.utils import constants

SECRET_KEY = secrets.token_hex(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(user_id: str, additional_claims: dict = None, expires_delta: timedelta = None):
    to_encode = {}
    now = datetime.now(timezone.utc)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "iss": constants.APP_NAME
    })
    
    if additional_claims:
        to_encode.update(additional_claims)
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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