# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database


db_dependency = Depends(database.get_db)

# User Routes
user_router = APIRouter(prefix="/users", tags=["Users"])

@user_router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = db_dependency):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)


@user_router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: int, db: Session = db_dependency):
    db_user = crud.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

'''
##########################
# Add to users.py
@user_router.get("/", response_model=list[schemas.UserResponse])
def read_users(db: Session = db_dependency):
    return db.query(models.User).all()

# Add to users.py
from datetime import datetime, timedelta
from jose import jwt

@user_router.post("/login")
def login(user: schemas.UserCreate, db: Session = db_dependency):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(db_user.user_id)}, 
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
'''