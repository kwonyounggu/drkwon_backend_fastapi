# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, database


db_dependency = Depends(database.get_db)

# Login History Routes
login_router = APIRouter(prefix="/login-history", tags=["Login History"])

@login_router.get("/user/{user_id}", response_model=list[schemas.LoginHistoryResponse])
def read_login_history(user_id: int, db: Session = db_dependency):
    return crud.get_login_history(db, user_id)


# Now you have API routes hooked up to your CRUD functions! 🚀