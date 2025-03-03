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