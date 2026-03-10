from psycopg2 import Date

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base
from datetime import datetime
from app.db.base import Base

AIBase = Base

class AIReservationAnalysis(AIBase):
    __tablename__ = "reservation_analysis"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    risk_score = Column(Float, nullable=False)
    decision = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
