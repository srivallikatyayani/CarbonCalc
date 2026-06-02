from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from app.database.session import get_db
from app.models.user import User
from app.core.security import verify_password
from app.schemas.user import UserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post(
    "/login",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Authenticate a user",
    description="Validates user credentials against PostgreSQL and returns user info.",
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
    
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )
        
    return user
