from sqlalchemy import Column, Integer, String, DateTime,Text, ForeignKey
from sqlalchemy.dialects.mysql.types import TINYINT
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Lead(Base):
    id = Column(Integer,primary_key=True)
    # country_code = Column(String(10))
    is_followup = Column(TINYINT,comment="1->active,2-completed,-1->inactive")
    name = Column(String(250))
    remarks = Column(Text)
    company_name = Column(String(250))
    contact_person = Column(String(250))
    lead_code = Column(String(200))
    phone = Column(String(20))
    alternative_no = Column(String(20))
    landline_number = Column(String(20))

    whatsapp_no = Column(String(20))
    email = Column(String(255))
    address = Column(Text)
    area = Column(String(200))
    customer_category_id = Column(Integer,ForeignKey("customer_category.id"))
    enquiry_type_id = Column(Integer,ForeignKey("enquiry_type.id"))
    lead_status_id = Column(Integer,ForeignKey("lead_status.id"))
    requirements_id = Column(String(255))
    refer_country_code = Column(String(10))

    approximate_amount = Column(String(50))
    country = Column(String(50))
    city = Column(String(50))
    states = Column(String(50))

    pincode = Column(String(10))
    dealer_id = Column(Integer,ForeignKey("user.id"))
    assigned_to = Column(Integer,ForeignKey("user.id"))
    deletedBy = Column(Integer,ForeignKey("user.id"))
    created_by =  Column(Integer,ForeignKey("user.id"))
    received_at = Column(DateTime)
    customer_id = Column(Integer,ForeignKey("user.id"))
    is_valid = Column(TINYINT,comment="1->valid,2->invalid")
    refered_by = Column(String(200))
    is_active = Column(TINYINT,comment="1->active,0->inactive")
    notes = Column(String(200))
    comments_description= Column(Text) 
    created_t = Column(DateTime)
    update_at = Column(DateTime)
    status = Column(TINYINT,comment="1->active,-1->deleted,0->inactive")
    is_transferred = Column(TINYINT,comment="1->yes,0->No")
    competitor_name = Column(String(250))
    competitor_id =Column(Integer,ForeignKey("competitors.id"))
    tempComment = Column(Text)
    schedule_date = Column(DateTime)
    poc_date = Column(DateTime)
    demo_date = Column(DateTime)
    transferComment = Column(Text) 
    refered_ph_no = Column(String(20))
    # follow_up_date = Column(DateTime)
    drop_reason = Column(Text)   
    lead_history = relationship("LeadHistory",back_populates="lead")
    customer_category = relationship("CustomerCategory",back_populates="lead")
    enquiry_type = relationship("EnquiryType",back_populates="lead")
    lead_status = relationship("LeadStatus",back_populates="lead")
    competitors = relationship("Competitors",back_populates="lead")

    # requirements = relationship("Requirements",back_populates="lead")
     
    dealer_user = relationship('User', foreign_keys=[dealer_id])
    deleted_by = relationship('User', foreign_keys=[deletedBy])
    create_user = relationship('User', foreign_keys=[created_by])
    assigned_user = relationship('User', foreign_keys=[assigned_to])
    customer = relationship('User', foreign_keys=[customer_id])
    lead_media = relationship('LeadMedia', back_populates="lead")
    follow_up = relationship('FollowUp', back_populates="lead")


    



