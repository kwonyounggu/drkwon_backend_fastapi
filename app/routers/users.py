# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models
from app.security import get_current_user
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
    db_user = crud.get_user_by_id(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.patch("/{user_id}/role", response_model=schemas.UserResponse)
def update_user_role(
    user_id: int,
    role_update: schemas.UserRoleUpdate,  # New schema
    db: Session = db_dependency,
    current_user: models.User = Depends(get_current_user)
):
    # Only allow admins or the user themselves to update the role
    if current_user.user_id != user_id and current_user.user_type != "admin": # type: ignore
        raise HTTPException(status_code=403, detail="Unauthorized")

    # Validate role input (optional but recommended)
    allowed_roles = {"admin", "od", "md" "general"}
    if role_update.new_role not in allowed_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role_update.new_role}")

    # Attempt to update user role
    user = crud.update_user_role(db, user_id, role_update.new_role)
    
    # Handle user not found case
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
