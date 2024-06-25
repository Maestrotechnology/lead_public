from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Media(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(Text)
    file_type = Column(TINYINT,comment="1-video,2-photo")
    requirement_id = Column(Integer,ForeignKey("requirements.id"))
    created_at = Column(DateTime)
    status = Column(TINYINT,comment="1->active,-1->deleted")
    
    requirements = relationship("Requirements",back_populates="media")
     
