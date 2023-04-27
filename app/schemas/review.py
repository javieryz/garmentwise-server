from pydantic import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String
from database.database import Base
from sqlalchemy.orm import relationship
from schemas.category import Category

class Review(Base):
  __tablename__ = 'reviews'

  id = Column(Integer, primary_key=True)
  dataset_id = Column(Integer, ForeignKey('datasets.id'))
  review_number = Column(Integer, unique=True)
  review_text = Column(String(length=1000))
  prediction = Column(Integer)
  fit_score = Column(Integer)
  color_score = Column(Integer)
  quality_score = Column(Integer)

  categories = relationship(
    "Category",
    secondary="review_categories",
    primaryjoin="Review.id == review_categories.c.review_id",
    secondaryjoin="Category.id == review_categories.c.category_id",
    backref="reviews"
  )

  class ReviewCreate(BaseModel):
    dataset_id: int
    review_number: int
    review_text: str
    prediction: int
    fit_score: int
    color_score: int
    quality_score: int