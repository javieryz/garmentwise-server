from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from schemas.user import User
from database.database import get_db

from services.auth_service import ACCESS_TOKEN_EXPIRE_MINUTES
from services.auth_service import user_exists, authenticate_user, create_access_token

router = APIRouter()

@router.post(
  "/login", 
  tags=["Authentication"],
  summary="Authenticates the user",
  description=  "Authenticates the user login using OAuth2 password grant type.\
                If successful, generates a Bearer token valid for 2 hours.",
  response_description="Bearer token",
  responses={
    200: {
      "content": {
        "application/json": {
          "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqeXoxQGdtYWlsLmNvbSIsImV4cCI6MTY4MjUyMzYwOH0.YJWVZrk5yGgMXjqVlCVWhG-nJY3thdZUXv-KtPzBUb4",
            "token_type": "Bearer",
            "expires_at": "2023-01-1T12:40:08.146917"
          }
        }
      }
    }
  }
)
async def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
  user = authenticate_user(email=form_data.username, password=form_data.password)
  if not user:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Invalid email or password",
      headers={"WWW-Authenticate": "Bearer"},
    )

  access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  access_token = create_access_token(
    data={"sub": user.email}, expires_delta=access_token_expires
  )

  response = {
    "access_token": access_token, 
    "token_type": "Bearer",
    "expires_at": datetime.now() + access_token_expires
  }
  return response

@router.post("/signup", tags=["Authentication"])
async def signup(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
  if user_exists:
    raise HTTPException(status_code=400, detail="Email address is already registered")

  user = User.create(db, email=form_data.username, password=form_data.password)
  response = await login(db, form_data)
  return response