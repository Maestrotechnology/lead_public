from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer,ForeignKey,DECIMAL,Text,DateTime,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Cities(Base):
    id=Column(Integer,primary_key=True)
    state_id=Column(Integer,ForeignKey("states.id"))
    name=Column(String(250))
    # district_id = Column(Integer, ForeignKey("districts.id"))
    
    # states=relationship("States",back_populates="cities")
    # user = relationship('User',back_populates="cities")
    # lead = relationship("Lead",back_populates="cities")
    # districts = relationship("Districts",back_populates="cities")

