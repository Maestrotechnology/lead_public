from sqlalchemy import Column, Integer,ForeignKey,CHAR,DECIMAL,Text,DateTime,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Country(Base):
    id = Column(Integer,primary_key = True)
    country_code = Column(String(10))
    name = Column(String(100))
    mobile_no_length = Column(String(50))
    iso = Column(CHAR(2))
    image = Column(String(255))
    sms_enabled =Column(TINYINT,comment ="1->active,-1->deleted" )
    status =Column(TINYINT,comment ="1->active,-1->deleted" )

