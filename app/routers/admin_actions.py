# API Routes for FastAPI with SQLAlchemy

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import crud, schemas, database


db_dependency = Depends(database.get_db)

# Admin Action Routes
admin_router = APIRouter(prefix="/admin-actions", tags=["Admin Actions"])

@admin_router.post("/", response_model=schemas.AdminActionResponse)
def create_admin_action(action: schemas.AdminActionRequest, admin_id: int, db: Session = db_dependency):
    return crud.create_admin_action(db, action, admin_id)


@admin_router.get("/admin/{admin_id}", response_model=list[schemas.AdminActionResponse])
def read_admin_actions(admin_id: int, db: Session = db_dependency):
    return crud.get_admin_actions(db, admin_id)