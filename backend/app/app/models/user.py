from sqlalchemy import Column, Integer, String, DateTime, ForeignKey,Text
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class User(Base):
    id = Column(Integer,primary_key=True)
    phone_country_code = Column(String(10))
    whatsapp_country_code = Column(String(10))
    alter_country_code = Column(String(10))
    user_type =Column(TINYINT,comment="1->superAdmin,2->Admin,2->Dealer,4->Employee,5->customer")
    name = Column(String(100))
    user_name = Column(String(100))
    email = Column(String(255))
    phone = Column(String(20))
    landline_number = Column(String(20))
    alternative_number =Column(String(20))
    whatsapp_no = Column(String(20))
    company_name = Column(String(250))
    address = Column(Text)
    area = Column(String(150))
    country = Column(String(50))
    states = Column(String(50))
    city = Column(String(50))

    pincode = Column(String(10))
    password = Column(String(255))
    dealer_id = Column(Integer,ForeignKey("user.id"))
    is_active = Column(TINYINT,comment = "1->active,0->inactive")
    image =Column(String(255))
    reset_key=Column(String(255))
    otp = Column(String(10))
    otp_expire_at = Column(DateTime)
    created_at=Column(DateTime)
    updated_at=Column(DateTime)
    status=Column(TINYINT,comment="-1->delete,1->active,0->inactive")

    api_tokens=relationship("ApiTokens",back_populates="user")
    dealer = relationship('User', remote_side=[id])

    lead_history = relationship("LeadHistory",back_populates="user")
    customer_category = relationship("CustomerCategory",back_populates="user")
    enquiry_type = relationship("EnquiryType",back_populates="user")
    lead_status = relationship("LeadStatus",back_populates="user")
    requirements = relationship("Requirements",back_populates="user")
    competitors = relationship("Competitors",back_populates="user")
    lead_media = relationship("LeadMedia",back_populates="user")
    follow_up = relationship("FollowUp",back_populates="user")


