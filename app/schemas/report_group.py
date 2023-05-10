from sqlalchemy import Column, ForeignKey, Integer, String
from database.database import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel

class ReportGroup(Base):
    __tablename__ = 'report_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    reports = relationship('Report', backref='report_group')

    class ReportGroupCreate(BaseModel):
        name: str
        user_id: int