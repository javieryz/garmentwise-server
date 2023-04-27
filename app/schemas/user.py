from sqlalchemy import Column, Integer, String, UniqueConstraint
from database.database import Base
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String)

    __table_args__ = (UniqueConstraint('email', name='unique_email'),)

    @classmethod
    def get_by_email(cls, email: str):
        db = next(get_db())
        return db.query(User).filter(User.email == email).first()

    @classmethod
    def create(cls, db: Session, email: str, password: str):
        hashed_password = pwd_context.hash(password)
        user = User(email=email, hashed_password=hashed_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user