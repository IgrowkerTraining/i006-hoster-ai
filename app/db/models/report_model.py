from sqlalchemy import Column, Integer, String, Date, DateTime,Text  
from app.db.base import Base
from datetime import datetime

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    report_date = Column(Date, nullable=False)
    analyzed_period = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)