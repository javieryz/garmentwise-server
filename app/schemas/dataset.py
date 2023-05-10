from pydantic import BaseModel, validator
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from datetime import date
from database.database import Base, DB_REPORT_TITLE_MAX_LENGTH
from sqlalchemy.orm import relationship

class Dataset(Base):
  __tablename__ = 'datasets'

  id = Column(Integer, primary_key=True)
  title = Column(String, unique=False, nullable=False)
  report_id = Column(Integer, ForeignKey('reports.id'))
  date = Column(Date)

  reviews = relationship('Review', backref='dataset')

  class DatasetCreate(BaseModel):
    title: str
    report_id: str
    date: date

    @validator('title')
    def preprocess_title(cls, title):
      if (len(title) > DB_REPORT_TITLE_MAX_LENGTH):
        title = title[:DB_REPORT_TITLE_MAX_LENGTH]
      return title