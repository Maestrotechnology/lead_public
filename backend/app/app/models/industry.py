from sqlalchemy import Column, Integer, String,Text, DateTime, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Industry(Base):
    id= Column(Integer,primary_key=True)
    name = Column(String(150))
    industry_type = Column(String(100))
    description = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(TINYINT,comment="1->active,-1->deleted")

   

