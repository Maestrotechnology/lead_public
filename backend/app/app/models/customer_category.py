from sqlalchemy import Column, Integer,ForeignKey,DECIMAL,Text,DateTime,String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT
from app.db.base_class import Base

class CustomerCategory(Base):
    __tablename__ = "customer_category"
    id = Column(Integer,primary_key =True)
    name = Column(String(150))
    created_by = Column(Integer,ForeignKey("user.id"))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    status = Column(TINYINT,comment = "1->active,-1->deleted")

    user = relationship("User",back_populates="customer_category")
    lead = relationship("Lead",back_populates="customer_category")

