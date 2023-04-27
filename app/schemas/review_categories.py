from sqlalchemy import Column, ForeignKey, Integer, Table
from database.database import Base

review_categories = Table('review_categories', Base.metadata,
    Column('review_id', Integer, ForeignKey('reviews.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))    
)