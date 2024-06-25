from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class LeadHistory(Base):
    __tablename__ = "lead_history"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer,ForeignKey("lead.id"))
    followup_id = Column(Integer,ForeignKey("follow_up.id"))
    leadStatus = Column(String(200))
    lead_status_id = Column(Integer,ForeignKey("lead_status.id"))
    enquiry_type_id = Column(Integer,ForeignKey("enquiry_type.id"))
    changedBy = Column(Integer,ForeignKey("user.id"))
    longitude = Column(String(200))
    latitude = Column(String(200))
    comment = Column(Text)
    created_at = Column(DateTime)
    status = Column(TINYINT,comment =" 1->active,-1->deleted")

    user = relationship("User",back_populates="lead_history")
    lead = relationship("Lead",back_populates="lead_history")
    lead_status = relationship("LeadStatus",back_populates="lead_history")
    lead_media = relationship("LeadMedia",back_populates="lead_history")
    follow_up = relationship("FollowUp",back_populates="lead_history")
    enquiry_type = relationship("EnquiryType",back_populates="lead_history")


