from typing import TYPE_CHECKING
from sqlalchemy import Column, Integer,ForeignKey,DECIMAL,Text,DateTime,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class Districts(Base):
    id = Column(Integer,primary_key=True)
    name = Column(String(150))
    # state_id = Column(Integer,ForeignKey("states.id"))
    status = Column(TINYINT,comment="1->active,-1->deleted")

    # states=relationship("States",back_populates="districts")
    # cities = relationship("Cities",back_populates="districts")
    # user = relationship("User",back_populates="districts")
    # lead = relationship("Lead",back_populates="districts")

