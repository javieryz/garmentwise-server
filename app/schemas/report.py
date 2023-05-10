from datetime import date
from sqlalchemy import Date, Column, Float, ForeignKey, Integer, LargeBinary, String
from schemas.dataset import Dataset
from database.database import Base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel

class Report(Base):
  __tablename__ = 'reports'

  id = Column(Integer, primary_key=True)
  title = Column(String, nullable=False)
  user_id = Column(Integer, ForeignKey('users.id'))
  report_group_id = Column(Integer, ForeignKey('report_groups.id'))
  date = Column(Date)
  overall_score = Column(Float)
  fit_score = Column(Float)
  color_score = Column(Float)
  quality_score = Column(Float)
  total_reviews = Column(Integer)
  fit_reviews = Column(Integer)
  color_reviews = Column(Integer)
  quality_reviews = Column(Integer)
  word_count = Column(JSONB)
  wordcloud = Column(LargeBinary)
  dataset = relationship('Dataset', backref='report')
    
  class ReportCreate(BaseModel):
    title: str
    user_id: int
    report_group_id: int
    date: date
    overall_score: float
    fit_score: float
    color_score: float
    quality_score: float
    total_reviews: int
    fit_reviews: int
    color_reviews: int
    quality_reviews: int
    wordcloud: bytes
    word_count: str
  
  @classmethod
  def create_report(cls, db: Session, report: ReportCreate):
    report_dict = report.dict()
    dataset_dict = report_dict.pop('dataset')
    report_obj = cls(**report_dict)
    dataset_obj = Dataset(**dataset_dict)
    report_obj.dataset = dataset_obj
    db.add(report_obj)
    db.commit()
    db.refresh(report_obj)
    return report_obj