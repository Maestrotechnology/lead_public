from sqlalchemy import Column, Integer,ForeignKey,CHAR,DECIMAL,Text,DateTime,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class WhatsappContent(Base):
    id = Column(Integer,primary_key = True)
    content = Column(Text)
    status =Column(TINYINT,comment ="1->active,-1->deleted" )   
    created_at=Column(DateTime)
    updated_at=Column(DateTime)

