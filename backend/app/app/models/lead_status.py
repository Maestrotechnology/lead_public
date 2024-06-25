from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class LeadStatus(Base):
    __tablename__ = "lead_status"
    id = Column(Integer,primary_key=True)
    name =  Column(String(200))
    created_by = Column(Integer,ForeignKey("user.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(TINYINT,comment= "1->active,-1->deleted")

    user = relationship("User",back_populates="lead_status")
    lead = relationship("Lead",back_populates="lead_status")
    lead_history = relationship("LeadHistory",back_populates="lead_status")


