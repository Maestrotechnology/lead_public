from sqlalchemy import Column, Integer, String,Text, DateTime, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class EnquiryType(Base):
    __tablename__ ="enquiry_type"
    id = Column(Integer,primary_key =True)
    name = Column(String(200))
    created_by = Column(Integer,ForeignKey("user.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(TINYINT)

    user = relationship("User",back_populates="enquiry_type")
    lead = relationship("Lead",back_populates="enquiry_type")
    lead_history = relationship("LeadHistory",back_populates="enquiry_type")
    follow_up = relationship("FollowUp",back_populates="enquiry_type")


