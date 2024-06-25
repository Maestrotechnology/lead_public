from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class FollowUp(Base):
    __tablename__ = "follow_up"
    id = Column(Integer, primary_key=True)
    lead_id = Column(Integer,ForeignKey("lead.id"))
    enquiry_type_id = Column(Integer,ForeignKey("enquiry_type.id"))

    createdBy = Column(Integer,ForeignKey("user.id"))
    comment = Column(Text)
    followup_dt = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    followup_status = Column(TINYINT,comment =" 1->follow_up,2-completed,-1->cancelled")
    status = Column(TINYINT,comment =" 1->active,-1->deleted")

    user = relationship("User",back_populates="follow_up")
    lead = relationship("Lead",back_populates="follow_up")
    lead_history = relationship("LeadHistory",back_populates="follow_up")
    lead_media = relationship("LeadMedia",back_populates="follow_up")
    enquiry_type = relationship("EnquiryType",back_populates="follow_up")


     
