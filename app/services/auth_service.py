from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from schemas.user import User
from database.database import get_db
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ACCESS_TOKEN_EXPIRE_MINUTES = 120

def user_exists(email: str, db: Session = Depends(get_db)):
  existing_user = db.query(User).filter(User.email == email).params(email=email).first()
  if existing_user:
    return True
  else:
    return False


def authenticate_user(email: str, password: str):
  user = User.get_by_email(email=email)
  if not user:
    return False
  if not pwd_context.verify(password, user.hashed_password):
    return False
  return user


def create_access_token(data: dict, expires_delta: timedelta = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=30)
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
  return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  try:
    payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    email: str = payload.get("sub")
    if email is None:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    user = db.query(User).filter(User.email == email).first()
    if user is None:
      raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")