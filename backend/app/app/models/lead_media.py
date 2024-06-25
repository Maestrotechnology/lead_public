from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class LeadMedia(Base):

    __tablename__="lead_media"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(Text)
    lead_id = Column(Integer,ForeignKey("lead.id"))
    followup_id = Column(Integer,ForeignKey("follow_up.id"))
    lead_history_id = Column(Integer,ForeignKey("lead_history.id"))
    created_at = Column(DateTime)
    upload_by=Column(Integer,ForeignKey("user.id"))
    status = Column(TINYINT,comment="1->active,-1->deleted")
    
    lead = relationship("Lead",back_populates="lead_media")
    lead_history = relationship("LeadHistory",back_populates="lead_media")
    user = relationship("User",back_populates="lead_media")
    follow_up = relationship("FollowUp",back_populates="lead_media")


     
