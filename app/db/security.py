from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from app.utils import constants
from app.db import schemas, crud, database

from sqlalchemy.orm import Session

'''
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    db: Session = Depends(database.get_db),
    token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM]) # type: ignore
        user_id: int = payload.get("sub") # type: ignore
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise credentials_exception
    return user
'''

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", auto_error=False)  # auto_error=False to avoid automatic 401

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[schemas.UserResponse]:
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, constants.SECRET_KEY, algorithms=[constants.ALGORITHM]) # type: ignore
        user_id: int = payload.get("sub") # type: ignore
        if user_id is None:
            return None
        # Fetch user from database (example)
        from app.db.crud import get_user_by_id
        from app.db.database import get_db
        db = next(get_db())
        user = get_user_by_id(db, user_id)
        if user is None:
            return None
        return schemas.UserResponse.from_orm(user)
    except JWTError:
        return None