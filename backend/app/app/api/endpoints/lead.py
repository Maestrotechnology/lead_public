from fastapi import APIRouter, Depends, Form,requests,UploadFile,File
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import *
from app.db.session import SessionLocal
from app.core import security
from typing import Optional,List,Union

router = APIRouter()

@router.post("/add_content")
async def addContent(db:Session=Depends(deps.get_db),
                     token:str = Form(...),content:str=Form(...)):
    
    user = deps.get_user_token(db=db , token=token)
    if user:
        getContent = db.query(WhatsappContent).filter(WhatsappContent.id==1).\
        update({"content":content,"updated_at":datetime.now(settings.tz_IN)})
        db.commit()

        return({"status":1,"msg":"Content Updated"})
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    
@router.post("/view_content")
async def viewContent(db:Session=Depends(deps.get_db),
                     token:str = Form(...)):
    
    user = deps.get_user_token(db=db , token=token)
    if user:
        getContent = db.query(WhatsappContent).filter(WhatsappContent.id==1).first()

        data={"content":getContent.content}

        return({"status":1,"msg":"Success","data":data})
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    
    
@router.post("/create_lead")
async def createLead(db:Session=Depends(deps.get_db),
                     token:str = Form(...),name:str=Form(...),
                     remarks:str=Form(None),
                     phone_country_code:str=Form(...),
                     landline_number:str=Form(None),
                     whatsapp_country_code:str=Form(None),
                     alter_country_code:str=Form(None),
                     company_name :str=Form(None),
                     contact_person:str=Form(None),
                     address:str=Form(...),
                     area:str=Form(None),
                     phone:str=Form(...),email:str=Form(None),
                     alternative_no:str=Form(None),whatsapp_no:str=Form(None),
                     customer_category_id:int = Form(None),
                     enquiry_type_id:int = Form(None),
                     requirements_id:str=Form(...),
                     state:str = Form(None),country:str=Form(None),city:str=Form(None),
                     dealer_id:int=Form(None),
                     assignedTo:int=Form(None),
                     receivedDate:datetime=Form(None),
                     referedBy:str = Form(None),referedPhone:str=Form(None),
                     refer_country_code:str=Form(None),notes:str=Form(None),
                     description:str=Form(None),isNew:int=Form(None),
                     latitude:str=Form(None),longitude:str=Form(None),
                     customerId:int=Form(None),Pincode:str=Form(None),
                     schedule_date:datetime=Form(None),
                    upload_file:Optional[Union[UploadFile,List[UploadFile]]] = File(default=None),
                     approximate_amount:str=Form(None)
                    ):
    
    user = deps.get_user_token(db=db , token=token)
    if user:
        if deps.contains_emoji(name):
            return {"status":0,"msg":"Emojis are not allowed to use."}
        if company_name:
            if deps.contains_emoji(company_name):
                return {"status":0,"msg":"Emojis are not allowed to use."}
        if contact_person:
            if deps.contains_emoji(contact_person):
                return {"status":0,"msg":"Emojis are not allowed to use."}
        if email:
            if deps.contains_emoji(email):
                return {"status":0,"msg":"Emojis are not allowed to use in email."}
        leadStatusID = 1
        dealer = None
        assignedUser= None
        getAllUsers = db.query(User).filter(User.status == 1)

        if user.user_type in [1,2]:

            if schedule_date:
                if schedule_date<datetime.now():
                        return{"status":0,"msg":"Only future datetime are allowed."}
            if dealer_id:
                checkDealerId = getAllUsers.filter(User.id == dealer_id,
                                                   User.user_type == 3).first()
                if not checkDealerId:
                    return {"status":0,"msg":"No dealer record found."}
                dealer = dealer_id
            else:
                dealer = None

        elif user.user_type == 3:
            dealer = user.id
            
        elif user.user_type == 4:
            dealer = user.dealer_id
            assignedUser = user.id
            leadStatusID = 2
        
        if user.user_type != 4:
            if not assignedTo :
                assignedUser = None
            else:
                checkUser = getAllUsers.filter(User.id == assignedTo,
                                                User.user_type==4).first()
                if not checkUser:
                    return {"status":0,"msg":"No employee record found."}
                else:
                    assignedUser = assignedTo
                    leadStatusID = 2
    
            
        checkuser = db.query(User).filter(User.status == 1)
        if isNew: 
            checkMobile = checkuser.filter(or_(User.phone==phone,
                                                    User.alternative_number ==phone,
                                                    User.whatsapp_no == phone)).first()
            if checkMobile :
                return {"status":0,"msg":"This mobile number already exists."}
            if alternative_no:
                if phone != alternative_no:
                    checkMobile = checkuser.filter(or_(User.phone==alternative_no,
                                                    User.alternative_number ==alternative_no,
                                                    User.whatsapp_no == alternative_no)).first()
                    if checkMobile :
                        return {"status":0,"msg":"This alternative mobile number already exists."}
                else:
                    return {"status":0,"msg":"Mobile number and alternative mobile number not to be same."}
            if  whatsapp_no:
                checkMobile = checkuser.filter(or_(User.phone==whatsapp_no,
                                                    User.alternative_number ==whatsapp_no,
                                                    User.whatsapp_no == whatsapp_no)).first()
                if checkMobile :
                    return {"status":0,"msg":"This whatsapp number already exists."}
                
                
        getAllReqId = [int(row) for row in requirements_id.split(",") ]

        # filter_conditions = [Lead.requirements_id.like(f"%{req}%") for req in getAllReqId]
        filter_conditions = [Lead.requirements_id.op('REGEXP')(rf'\b{req}\b') for req in getAllReqId]


        combined_filter = or_(*filter_conditions)

        today = datetime.now(settings.tz_IN).date()

        sameReqLead = db.query(Lead).filter(
            Lead.status==1,combined_filter,
            cast(Lead.created_t,Date)==today)
        
        
        existNumber = sameReqLead.filter(or_(Lead.phone==phone,
                Lead.alternative_no ==phone,
                Lead.whatsapp_no==phone,)).first()
        
        if existNumber:
            return {"status":0,"msg":"This Requirement already exists With Same Phone Number."}
        
        if whatsapp_no:

            existWtsNumber = sameReqLead.filter(or_(Lead.phone==whatsapp_no,
                Lead.alternative_no ==whatsapp_no,
                Lead.whatsapp_no==whatsapp_no,)).first()
            
            if existWtsNumber:
                return {"status":0,"msg":"This Requirement already exists With Same Whatsapp Number."}
            
        if alternative_no:

            existAltNumber = sameReqLead.filter(or_(Lead.phone==alternative_no,
                Lead.alternative_no ==alternative_no,
                Lead.whatsapp_no==alternative_no,)).first()
            
            if existAltNumber:
                return {"status":0,"msg":"This Requirement already exists With Same alternative Number."}

            
        if customer_category_id: 
            checkCategory = db.query(CustomerCategory).filter(CustomerCategory.id == customer_category_id,
                                                              CustomerCategory.status ==1 ).first()

            if not checkCategory:
                return {"status":0,"msg":"Invalid customer category"}
            
        if enquiry_type_id:
            checkEnquiry = db.query(EnquiryType).filter(EnquiryType.id == enquiry_type_id,
                                                        EnquiryType.status ==1).first()
            if not checkEnquiry:
                return {"status":0,"msg":"Invalid Enquiry type "}
        
        
        checkRequirementsId = db.query(Requirements).filter(Requirements.id.in_(getAllReqId),
                                                   Requirements.status ==1).first()
        isvalid = 1
        if not checkRequirementsId:
            return {"status":0,"msg":"Invalid Requirement"}
        # print(getAllReqId)
        if 20 in getAllReqId:
            # print("PResent")
            leadStatusID = 17      

        if not isNew:
            customer = customerId
        else:
            createNewUser = User(
               user_type =5,
               name = name,
               phone_country_code = phone_country_code,
               whatsapp_country_code = whatsapp_country_code,
               alter_country_code = alter_country_code,
               user_name = contact_person,
               landline_number=landline_number,

               phone = phone,
               alternative_number = alternative_no,
               whatsapp_no = whatsapp_no,
               address = address,
               area = area,
               states = state,
               city = city,
               country = country,
               pincode = Pincode,
               created_at = datetime.now(settings.tz_IN),
               status =1,
               email = email,
               company_name = company_name,
               is_active = 1
            )

            db.add(createNewUser)
            db.commit()

            customer = createNewUser.id

        today = datetime.now(settings.tz_IN)
        createNewLead = Lead(
            name = name,
            remarks = remarks,
            customer_id = customer ,
            company_name = company_name,
            contact_person = contact_person,
            lead_code =0,
            phone = phone,
            alternative_no = alternative_no,
            whatsapp_no = whatsapp_no,
            address =address,
            area = area,
            customer_category_id =customer_category_id,
            enquiry_type_id = enquiry_type_id,
            requirements_id = requirements_id,
            email = email,
            states = state,
            city = city,
            country = country,
            approximate_amount =approximate_amount,
            landline_number=landline_number,

            pincode = Pincode,
            lead_status_id = leadStatusID,
            dealer_id = dealer,
            assigned_to = assignedUser,
            received_at = receivedDate or today ,
            refered_by = referedBy,
            refer_country_code = refer_country_code,
            refered_ph_no = referedPhone,
            is_active = 0,
            notes = notes,
            comments_description = description,
            created_t = today,
            created_by = user.id,
            update_at = today,
            is_valid = isvalid,
            status = 1,
            schedule_date = schedule_date )
        
        db.add(createNewLead)
        db.commit()

        newLeadName = "Lead"+str(createNewLead.id)
        createNewLead.lead_code = newLeadName
        db.commit()

        historyId = None
        followupId = None

        comment = "Created" 
        if schedule_date:
            comment = f"Created (The follow-up date is scheduled for {schedule_date.strftime('%Y-%m-%d %H:%M')})"
            newFollowUp = FollowUp(
                lead_id= createNewLead.id,
                followup_dt = schedule_date,
                createdBy = user.id,
                comment = comment,
                followup_status = 1,
                created_at = datetime.now(settings.tz_IN),
                status = 1 )
            
            createNewLead.is_followup=1
            db.add(newFollowUp)
            db.commit()
            followupId=newFollowUp.id


            addHistory = LeadHistory(
                lead_id= createNewLead.id,
                followup_id = newFollowUp.id,
                leadStatus = "Follow up",
                lead_status_id =5,
                changedBy= user.id,
                comment = comment,
                created_at = datetime.now(settings.tz_IN),
                status = 1
            )
            db.add(addHistory)
            db.commit()
            historyId = addHistory.id
            

        if not schedule_date:

            createLeadHistory =  LeadHistory(
                lead_id = createNewLead.id,
                leadStatus = "Unassigned" if leadStatusID == 1 else "Assigned" if leadStatusID == 2 else "Not valid",
                lead_status_id = leadStatusID,
                changedBy = user.id,
                created_at = today,
                longitude = longitude,
                latitude = latitude,
                comment =comment,
                status=1   )
            db.add(createLeadHistory)
            db.commit()

            historyId = createLeadHistory.id

        if upload_file and upload_file != None:
            if isinstance(upload_file, list):
                    
                for i in range(len(upload_file)):  
                    
                    store_fname = upload_file[i].filename
                    
                    f_name,*etn = store_fname.split(".")
                
                    file_path,file_exe = file_storage(upload_file[i],f_name)
                    add_file = LeadMedia(
                        lead_id = createNewLead.id,
                        url =file_exe,
                        lead_history_id = historyId,
                        followup_id =followupId,
                        created_at = datetime.now(tz=settings.tz_IN),
                        upload_by = user.id,
                        status = 1,
                    )  
                    db.add(add_file)  
                    db.commit()  
            else:
                store_fname = upload_file.filename
                    
                f_name,*etn = store_fname.split(".")
                file_path,file_exe = file_storage(upload_file,f_name)
                add_file = LeadMedia(
                        lead_id = createNewLead.id,
                        url =file_exe,
                        lead_history_id = historyId,
                        followup_id =followupId,
                        created_at = datetime.now(tz=settings.tz_IN),
                        upload_by = user.id,
                        status = 1,
                    )  
                db.add(add_file)  
                db.commit()  


        if dealer_id and user.user_type in [1,2]:
            getEmp = db.query(User).filter(User.id==dealer_id).first()
            if getEmp:
                sender_id = [getEmp.id]
                msg = {
                    "msg_title": "Maestro Sales",
                    "msg_body": "New Lead has been assigned to you.",
                }
                message_data = {"lead_id":createNewLead.id,"id":2}

                PushNotidy = send_push_notification(
                    db, sender_id, msg, message_data
                )

        if assignedTo:
            getEmp = db.query(User).filter(User.id==assignedTo).first()
            if getEmp:
                sender_id = [getEmp.id]
                msg = {
                    "msg_title": "Maestro Sales",
                    "msg_body": "New Lead has been assigned to you.",
                }
                message_data = {"lead_id":createNewLead.id,"id":2}

                PushNotidy = send_push_notification(
                    db, sender_id, msg, message_data
                )

        return({"status":1,"msg":"Lead record successfully created"})
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}

 
@router.post("/lead_update")
async def UpdateLead(db:Session = Depends(deps.get_db),
                     token:str = Form(...),
                     leadId: int = Form(...),
                     remarks:str=Form(None),
                     name:str=Form(...),
                     landline_number:str=Form(None),
                     phone_country_code:str=Form(...),
                     whatsapp_country_code:str=Form(None),
                     alter_country_code:str=Form(None),
                     refer_country_code:str=Form(None),
                     company_name :str=Form(None),
                     contact_person:str=Form(None),
                     address:str=Form(...),
                     area:str=Form(None),
                     phone:str=Form(...),email:str=Form(None),
                     alternative_no:str=Form(None),whatsapp_no:str=Form(None),
                     customer_category_id:int = Form(None),
                     enquiry_type_id:int = Form(None),
                     requirements_id:str=Form(...),
                     state:str = Form(None),city:str=Form(None),
                     country:str=Form(None),
                     dealer_id:int=Form(None),
                     assignedTo:int=Form(None),
                     receivedDate:datetime=Form(None),
                     referedBy:str = Form(None),notes:str=Form(None),
                     description:str=Form(None),
                     latitude:str=Form(None),
                     longitude:str=Form(None),Pincode:str=Form(None),
                     historyComment: str = Form(None),
                     schedule_date : datetime = Form(None),
                     referedPhone : str = Form(None),
                    upload_file:Optional[List[UploadFile]] = File(default=None),
                     approximate_amount:str=Form(None)
                     ):
    user = deps.get_user_token(db=db,token=token)
    if user:
        dealer = None
        dealerChange = 0
        today = datetime.now(settings.tz_IN).date()
        checkLead = db.query(Lead).filter(Lead.id == leadId,
                                          Lead.status == 1).first()
        if not checkLead:
            return {"status":0,"msg":"No lead record found."}
        
        getAllUsers = db.query(User).filter(User.status ==1)
        assignedUser= None
        if user.user_type in [1,2]:
            if dealer_id:

                checkDealerId = getAllUsers.filter(User.id == dealer_id,
                                                   User.user_type == 3).first()
                if not checkDealerId:
                    return {"status":0,"msg":"No dealer record found."}
                dealer = dealer_id
                if dealer_id != checkLead.dealer_id:
                    lead_status_id = 1
                    dealerChange = 1
                    assignedUser= None
            else:
                dealer = None
            db.commit()

        elif user.user_type == 3:
            dealer = user.id


        elif user.user_type ==4:
            dealer = user.dealer_id
            assignedUser = user.id

        if not assignedTo:
            assignedTo = None
        else:
            checkUser = getAllUsers.filter(User.id == assignedTo,
                                            User.user_type==4).first()
            if not checkUser:
                return {"status":0,"msg":"No employee record found."}
            else:
                assignedUser = assignedTo

        
        checkUser = db.query(User).filter(User.status == 1)

        getAllReqId = [int(row) for row in requirements_id.split(",") ]

        # filter_conditions = [Lead.requirements_id.like(f"%{req}%") for req in getAllReqId]
        filter_conditions = [Lead.requirements_id.op('REGEXP')(rf'\b{req}\b') for req in getAllReqId]


        combined_filter = or_(*filter_conditions)

        sameReqLead = db.query(Lead).filter(
            Lead.status==1,Lead.id !=leadId,combined_filter,cast(Lead.created_t,Date)==today)   
        
        existNumber = sameReqLead.filter(or_(Lead.phone==phone,
                Lead.alternative_no ==phone,
                Lead.whatsapp_no==phone,)).first()
        
        if existNumber:
            return {"status":0,"msg":"This Requirement already exists With Same Phone Number."}
        
        if whatsapp_no:

            existWtsNumber = sameReqLead.filter(or_(Lead.phone==whatsapp_no,
                Lead.alternative_no ==whatsapp_no,
                Lead.whatsapp_no==whatsapp_no,)).first()
            
            if existWtsNumber:
                return {"status":0,"msg":"This Requirement already exists With Same Whatsapp Number."}
            
        if alternative_no:

            existAltNumber = sameReqLead.filter(or_(Lead.phone==alternative_no,
                Lead.alternative_no ==alternative_no,
                Lead.whatsapp_no==alternative_no,)).first()
            
            if existAltNumber:
                return {"status":0,"msg":"This Requirement already exists With Same alternative Number."}
            
        
        getUserId = checkUser.filter(User.id == checkLead.customer_id ).first()
        
        getUser = checkUser.filter(User.id != checkLead.customer_id)

        if customer_category_id: 
            checkCategory = db.query(CustomerCategory).filter(CustomerCategory.id == customer_category_id,
                                                              CustomerCategory.status ==1 ).first()

            if not checkCategory:
                return {"status":0,"msg":"Invalid customer category"}
            
        if enquiry_type_id:
            checkEnquiry = db.query(EnquiryType).filter(EnquiryType.id == enquiry_type_id,
                                                        EnquiryType.status ==1).first()
            if not checkEnquiry:
                return {"status":0,"msg":"Invalid Enquiry type "}
            
        getReqData = [int(row) for row in requirements_id.split(",")]
        getReqData1=None
        if checkLead.requirements_id:
            getReqData1 = [int(row) for row in checkLead.requirements_id.split(",")]
        lead_status_id = None
        if dealerChange:
            lead_status_id = 1

        if assignedTo!= checkLead.assigned_to:
            lead_status_id = 2
        if 20 in getReqData:
            lead_status_id = 17
        elif getReqData1 and 20 in getReqData1:
            if 20 not in  getReqData:
                if checkLead.assigned_to:
                    lead_status_id = 2
                else:
                    lead_status_id = 1        
        checkRequirementsId = db.query(Requirements).filter(Requirements.id.in_(getReqData),
                                                   Requirements.status ==1).first()
        isvalid = 1
        if not checkRequirementsId:
            return {"status":0,"msg":"Invalid Requirement"}
        today = datetime.now(settings.tz_IN)
       
        checkLead.name = name
        checkLead.company_name =company_name
        checkLead.contact_person = contact_person
        checkLead.phone = phone
        checkLead.remarks = remarks
        checkLead.alternative_no = alternative_no
        checkLead.whatsapp_no =whatsapp_no
        checkLead.address =address,
        checkLead.area = area,
        checkLead.customer_category_id =customer_category_id,
        checkLead.enquiry_type_id = enquiry_type_id,
        checkLead.requirements_id = requirements_id,
        checkLead.email = email
        checkLead.landline_number = landline_number
        checkLead.states = state
        checkLead.city = city
        checkLead.country = country
        checkLead.pincode = Pincode
        checkLead.dealer_id = dealer
        checkLead.assigned_to = None if dealerChange==1 else assignedUser
        checkLead.is_valid = isvalid
        checkLead.received_at = receivedDate
        checkLead.refer_country_code = refer_country_code
        checkLead.refered_by = referedBy
        checkLead.notes = notes
        checkLead.comments_description = description
        checkLead.update_at = today
        checkLead.approximate_amount =approximate_amount if approximate_amount else checkLead.approximate_amount,
        checkLead.lead_status_id = lead_status_id if lead_status_id else checkLead.lead_status_id
        checkLead.schedule_date = schedule_date
        checkLead.refered_ph_no = referedPhone

        db.commit()

        getCustomer = db.query(User).filter(User.id==checkLead.customer_id).first()

        if getCustomer:
            getCustomer.name = name
            getCustomer.user_name = contact_person
            getCustomer.phone = phone
            getCustomer.phone_country_code = phone_country_code
            getCustomer.whatsapp_country_code = whatsapp_country_code
            getCustomer.alter_country_code = alter_country_code
            getCustomer.alternative_number = alternative_no
            getCustomer.whatsapp_no = whatsapp_no
            getCustomer.address = address
            getCustomer.landline_number = landline_number
            getCustomer.area = area
            getCustomer.states_id = state
            getCustomer.cities_id = city
            getCustomer.pincode = Pincode
            getCustomer.updated_at = datetime.now(settings.tz_IN)
            getCustomer.email = email
            getCustomer.company_name = company_name
        db.commit()
        
        createLeadHistory =  LeadHistory(
            lead_id = leadId,
            lead_status_id = checkLead.lead_status_id,
            leadStatus = checkLead.lead_status.name,
            longitude = longitude,
            latitude = latitude,
            changedBy = user.id,
            comment = historyComment or "No reason",
            created_at = today,
            status=1 )
        db.add(createLeadHistory)
        db.commit()


        if upload_file and upload_file != None:
                    
            for i in range(len(upload_file)):  
                
                store_fname = upload_file[i].filename
                
                f_name,*etn = store_fname.split(".")
            
                file_path,file_exe = file_storage(upload_file[i],f_name)
                add_file = LeadMedia(
                    lead_id = checkLead.id,
                    url = file_exe,
                    lead_history_id = createLeadHistory.id,
                    created_at = datetime.now(tz=settings.tz_IN),
                    upload_by = user.id,
                    status = 1,
                )  
                db.add(add_file)  
                db.commit()  

        return {"status":1,"msg":"Lead record successfully updated."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/list_lead")
async def leadList(db:Session = Depends(deps.get_db),
                     token:str = Form(...),page:int =1,size:int =10,
                     phone:str=Form(None),name:str=Form(None),globalName:str=Form(None),
                     leadBy:int=Form(None),lead_status:int=Form(None),
                     state:str=Form(None),country:str=Form(None),
                     city:str=Form(None),
                     is_deleted:int=Form(None,description="1->show deleted"),
                     lead_id:str=Form(None),
                     attentionSeek:int=Form(None,description="1->need attention"),
                     fromdatetime:date=Form(None),
                     todatetime:date=Form(None),
                     lead_code:str=Form(None),type:int=Form(None,description='1->all,2->Assigned,3->Quotation,4->Followup,5->Orders,6->Missed'),
                     employeeId:int=Form(None),dealerId:int=Form(None),
                     is_web:int=Form(None),
                     is_reminder:int=Form(None,description="1->reminderList"),
                     hot_lead:int=Form(None),

                     ):
    user = deps.get_user_token(db=db,token=token)
    if user:

        today = datetime.now(settings.tz_IN)
        todayDt = datetime.now()
        missedDays=None
        remainingDays=None


        if is_reminder:
            lead_status=5
            fromdatetime = datetime.now(settings.tz_IN).strftime("%Y-%m-%d 00:00:00")
            todatetime = (datetime.now(settings.tz_IN) + timedelta(days=5)).strftime("%Y-%m-%d 23:59:59")
        
        getAllLead = db.query(Lead)
                                           
        if not is_reminder:

            if todatetime == None:
                todatetime = today.replace(day=31,month=12).strftime("%Y-%m-%d 23:59:59")
            else:
                todatetime = todatetime.strftime("%Y-%m-%d 23:59:59")
            
            if fromdatetime == None:
                fromdatetime = today.replace(day=1,month=1).strftime("%Y-%m-%d 00:00:00")
            else:
                fromdatetime = fromdatetime.strftime("%Y-%m-%d 00:00:00")
                
            # getAllLead = getAllLead.filter(Lead.update_at.between(fromdatetime,todatetime))
            if lead_status not in [5,9]:
                getAllLead = getAllLead.filter(Lead.update_at.between(fromdatetime,todatetime))
            else:
                getAllLead = getAllLead.filter(Lead.schedule_date.between(fromdatetime,todatetime))



        # else:
        #     getAllLead = getAllLead.filter(Lead.schedule_date.between(fromdatetime,todatetime))
        status=1
        if is_deleted==1:
            status=0

        getAllLead = getAllLead.filter(Lead.status==status)


        if globalName:
            getAllLead = getAllLead.filter(or_(Lead.name.like("%"+globalName+"%"),
                                    Lead.company_name.like("%"+globalName+"%"),
                                    Lead.contact_person.like("%"+globalName+"%"),
                                    Lead.lead_code.like("%"+globalName+"%"),
                                    Lead.phone.like("%"+globalName+"%"),
                                    Lead.alternative_no.like("%"+globalName+"%"),
                                    Lead.whatsapp_no.like("%"+globalName+"%"),
                                    Lead.email.like("%"+globalName+"%"),
                                    Lead.landline_number.like("%"+globalName+"%"),

                                    ))

                    
        getAllLead1 = getAllLead

        if type not in [5,9]:

            if not type or type == 1:
                getAllLead = getAllLead
            else:
                getAllLead = getAllLead.filter(Lead.lead_status_id == type)   
        

        if user.user_type == 3:
            getAllLead = getAllLead.filter(Lead.dealer_id == user.id,Lead.lead_status_id !=17)
            
        elif user.user_type == 4:
            getAllLead = getAllLead.filter(Lead.assigned_to == user.id,Lead.lead_status_id !=17)

        if lead_id:
            leadIds = lead_id.split(',')
            getAllLead = getAllLead.filter(Lead.id.in_(leadIds))

        if phone:
            getAllLead = getAllLead.filter(Lead.phone.like("%"+phone+"%"))
        if name:
            getAllLead = getAllLead.filter(Lead.name.like("%"+name+"%"))
        if leadBy:
            getAllLead = getAllLead.filter(Lead.enquiry_type_id==leadBy)
        if lead_status and lead_status not in [5,9] :
            getAllLead = getAllLead.filter(Lead.lead_status_id==lead_status)
        if lead_status==5:
            getAllLead = getAllLead.filter(Lead.is_followup==1)
        if lead_status!=7:
            getAllLead = getAllLead.filter(Lead.lead_status_id!=7)

        if lead_status==9:
            # getAllLead = getAllLead.filter(Lead.lead_status_id==5,(func.DATE(Lead.schedule_date) < today))
            getAllLead = getAllLead.filter(Lead.is_followup==1,(func.DATE_FORMAT(Lead.schedule_date, '%Y-%m-%d %H:%M') < today.strftime('%Y-%m-%d %H:%M')))
            

        if state:
            getAllLead = getAllLead.filter(Lead.states.like("%"+state+"%"))  
        if country:
            getAllLead = getAllLead.filter(Lead.country.like("%"+country+"%"))
        if city:
            getAllLead = getAllLead.filter(Lead.city.like("%"+city+"%"))
        if lead_code:
            getAllLead = getAllLead.filter(Lead.lead_code.like("%"+lead_code+"%"))
        if dealerId:
            getAllLead = getAllLead.filter(Lead.dealer_id == dealerId)
        if employeeId:
            getAllLead = getAllLead.filter(Lead.assigned_to == employeeId)
        if hot_lead:
            getAllLead  = getAllLead.filter(Lead.is_active==1 )



        dataList =[]
        count = 0
        if is_reminder:
            leadStatusData =[6,7,17]

            getAllLead = getAllLead.filter(Lead.lead_status_id.notin_(leadStatusData))
    
            getAllLead = getAllLead.order_by(
            case((Lead.is_followup == 1, 0), else_=1).asc(),
            case((Lead.is_followup == 1, Lead.schedule_date), else_=None).asc(),
            case((Lead.is_followup != 1, Lead.created_t), else_=None).desc()
        )

            totalCount = getAllLead.count()
            totalPage,offset,limit = get_pagination(totalCount,page,size)
            getAllLead = getAllLead.offset(offset).limit(limit).all()
            if getAllLead:

                for row in getAllLead:
                    files=[]
                    getFiles= db.query(LeadMedia).filter(LeadMedia.lead_id==row.id,
                                                         LeadMedia.status==1).all()
                    getFollowUp = db.query(FollowUp).filter(FollowUp.lead_id == row.id,
                                                             FollowUp.status == 1)
                    
                    
                    getFollowUp = getFollowUp.order_by(FollowUp.id.desc()).first()
                    
                    
                    for file in getFiles:
                        files.append({
                            "file_id":file.id,
                            "url":f"{settings.BASE_DOMAIN}{file.url}",
                            "lead_history_id":file.lead_history_id

                        })
                    dueType=0
                    if row.schedule_date and row.is_followup==1:
                    # if row.schedule_date and row.lead_status_id==5:
                        if row.schedule_date.strftime('%Y-%m-%d %H:%M')<todayDt.strftime('%Y-%m-%d %H:%M'):
                            dueType = -1
                            missedDays=(todayDt-row.schedule_date).days
                        elif row.schedule_date.strftime('%Y-%m-%d %H:%M')==todayDt.strftime('%Y-%m-%d %H:%M') or (row.schedule_date>todayDt and row.schedule_date.date()==todayDt.date()):
                            dueType = 1
                            remainingDays=0
                        elif row.schedule_date.strftime('%Y-%m-%d %H:%M')>todayDt.strftime('%Y-%m-%d %H:%M'):
                            dueType = 2        
                            remainingDays=(row.schedule_date-todayDt).days       


                    dataList.append({
                        "deleted_by":row.deleted_by.user_name if row.deletedBy else None,
                        "followup_enquiry_type":getFollowUp.enquiry_type.name if getFollowUp and getFollowUp.enquiry_type_id else None,
                        "followup_enquiry_id":getFollowUp.enquiry_type_id if getFollowUp  else None,                        "is_followup":row.is_followup,
                        "due_type":dueType,
                        "remarks":row.remarks,
                        "leadCode":row.lead_code,
                        "leadId":row.id,
                        "landline_number":row.landline_number,
                        "missed_days":missedDays,
                        "remaining_days":remainingDays,

                        "refer_country_code":row.refer_country_code  ,
                        "phone_country_code":row.customer.phone_country_code if row.customer_id else None ,
                        "whatsapp_country_code":row.customer.whatsapp_country_code if row.customer_id else None,
                        "alter_country_code":row.customer.alter_country_code if row.customer_id else None,
                        "customer_name":row.contact_person,
                        "leadName":row.name,
                        "companyName":row.company_name,
                        "employee_id":row.assigned_to,
                        "assignedTo":row.assigned_user.name if row.assigned_to else (row.dealer_user.name if row.dealer_id  and row.lead_status_id!=1 else None),
                        "email":row.email,

                        "mobile":row.phone,
                        "whatsapp_no":row.whatsapp_no if row.whatsapp_no else None,
                        "city":row.city,
                        "state":row.states,
                        "country":row.country,
                        "area":row.area,
                        "address":row.address,
                        "pincode":row.pincode,
                        "activeStatus":row.is_active,
                        "schedule_date":row.schedule_date,
                        "demo_date":row.demo_date,
                        "poc_date":row.poc_date,
                        "created_at":row.created_t,
                        "created_by":row.dealer_user.user_name if row.dealer_id else None,
                        "files":files,
                        "approximate_amount":row.approximate_amount,
                        "drop_reason":row.drop_reason,
                        "created_by_id":row.created_by,

                        "created_at":row.created_t,
                        "created_by":row.create_user.user_name if row.created_by else None,
                    })
                    missedDays=None
                    remainingDays=None
                # print(dataList)
            data=({"page":page,"size":size,
                   "total_page":totalPage,
                   "total_count":totalCount,
                   "items":dataList,
                    "attentionCount":count})
            return ({"status":1,"msg":"Success","data":data})

        threshold_datetime = datetime.now(settings.tz_IN)
        # threshold_datetime = datetime.now(settings.tz_IN) - timedelta(hours=24)
        leadStatusData =[6,7,17]

        getAllLeadData = getAllLead1.filter(Lead.lead_status_id.notin_(leadStatusData),
                        Lead.schedule_date <= threshold_datetime)

        if user.user_type == 3:
            getAllLeadData = getAllLeadData.filter(Lead.dealer_id == user.id)

        # getAllLeadData = getAllLeadData.order_by(Lead.lead_status_id.desc())
        # count = getAllLeadData.count()
        # allData = getAllLeadData.all()
        # allLeadId = [row.id for row in allData ]

        # if is_web:
        #     getAllLead = getAllLead.filter(
        #                 Lead.id.notin_(allLeadId)).order_by(Lead.schedule_date)
           
        # else:        
        #     getAllLead = getAllLead.order_by(Lead.schedule_date)
        # getAllLead = getAllLead.order_by(Lead.schedule_date.asc())

        getAllLead = getAllLead.order_by(
            case((Lead.is_followup == 1, 0), else_=1).asc(),
            case((Lead.is_followup == 1, Lead.schedule_date), else_=None).asc(),
            case((Lead.is_followup != 1, Lead.created_t), else_=None).desc()
        )

        totalCount = getAllLead.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllLead = getAllLead.offset(offset).limit(limit).all()

        if getAllLead:
            for row in getAllLead:
                files=[]
                getFiles= db.query(LeadMedia).filter(LeadMedia.lead_id==row.id,
                                                        LeadMedia.status==1).all()
                
                for file in getFiles:
                    files.append({
                        "file_id":file.id,
                        "url":f"{settings.BASE_DOMAIN}{file.url}",
                        "lead_history_id":file.lead_history_id

                    })
                getFollowUp = db.query(FollowUp).filter(FollowUp.lead_id == row.id,
                                                             FollowUp.status == 1)
                    
                    
                getFollowUp = getFollowUp.order_by(FollowUp.id.desc()).first()
            
                dueType=0
                if row.schedule_date and row.is_followup==1:
                # if row.schedule_date and row.lead_status_id==5:
                    if row.schedule_date.strftime('%Y-%m-%d %H:%M')<todayDt.strftime('%Y-%m-%d %H:%M'):
                        dueType = -1
                        missedDays=(todayDt-row.schedule_date).days
                        

                    # elif row.schedule_date.strftime('%Y-%m-%d %H:%M')==todayDt.strftime('%Y-%m-%d %H:%M'):
                    elif row.schedule_date.strftime==todayDt.strftime('%Y-%m-%d %H:%M') or (row.schedule_date>todayDt and row.schedule_date.date()==todayDt.date()):

                        dueType = 1
                        remainingDays=0

                    elif row.schedule_date.strftime('%Y-%m-%d %H:%M')>todayDt.strftime('%Y-%m-%d %H:%M'):
                        dueType = 2
                        remainingDays=(row.schedule_date-todayDt).days       


                dataList.append(
                    {
                        "deleted_by":row.deleted_by.user_name if row.deletedBy else None,

                          "followup_enquiry_type":getFollowUp.enquiry_type.name if getFollowUp and getFollowUp.enquiry_type_id else None,
                        "followup_enquiry_id":getFollowUp.enquiry_type_id if getFollowUp  else None,
                        "is_followup":row.is_followup,
                        "remarks":row.remarks,
                        "due_type":dueType,
                        "leadCode":row.lead_code,
                        "remarks":row.remarks,
                        "leadId":row.id,
                        "leadName":row.name,
                        "companyName":row.company_name,
                        "email":row.email,
                        "customer_name":row.contact_person,
                        "remaining_days":remainingDays,
                        "mobile":row.phone,
                        "city":row.city,
                        "state":row.states,
                        "refer_country_code":row.refer_country_code  ,
                        "country":row.country,
                        "phone_country_code":row.customer.phone_country_code if row.customer_id else None,
                        "whatsapp_country_code":row.customer.whatsapp_country_code if row.customer_id else None,
                        "alter_country_code":row.customer.alter_country_code if row.customer_id else None,
                        "area":row.area,
                        "address":row.address,
                        "pincode":row.pincode,
                        "whatsapp_no":row.whatsapp_no if row.whatsapp_no else None,
                        "landline_number":row.landline_number,
                        "competitorName":row.competitor_name,
                        "competitor_id":row.competitor_id,
                        "dealerId":row.dealer_id,
                        "dealerName":row.dealer_user.name if row.dealer_id else None,
                        "dealerActiveStatus":row.dealer_user.is_active if row.dealer_id  else None,
                        "employee_id":row.assigned_to,
                        "assignedTo":row.assigned_user.name if row.assigned_to else (row.dealer_user.name if row.dealer_id  and row.lead_status_id!=1 else None),
                        "employeeActiveStatus": row.assigned_user.is_active if row.assigned_to  else None,
                        "receivedAt":row.received_at.strftime("%Y-%m-%d %H:%M:%S") if row.received_at else None,
                        "isActive":row.is_active,
                        "leadStatusId":row.lead_status_id,
                        "leadStatusName":row.lead_status.name if row.lead_status_id else None,
                        "leadComment":row.tempComment,
                        "schedule_date":row.schedule_date,
                        "demo_date":row.demo_date,
                        "missed_days":missedDays,
                        "poc_date":row.poc_date,
                        'transferComment':row.transferComment,
                        "referNumber":row.refered_ph_no,
                        "referName":row.refered_by,
                        "activeStatus":row.is_active,
                        "approximate_amount":row.approximate_amount,
                        "drop_reason":row.drop_reason,
                        "created_at":row.created_t,
                        "created_by_id":row.created_by,

                        "created_by":row.create_user.user_name if row.created_by else None,
                        "files":files

                    }
                )
                missedDays=None
                remainingDays=None
        data=({"page":page,"size":size,
                   "total_page":totalPage,
                   "total_count":totalCount,
                   "items":dataList,
                   "attentionCount":count})
        return ({"status":1,"msg":"Success","data":data})
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/attention_lead")
async def attentionLead(db:Session = Depends(deps.get_db),
                     token:str = Form(...),page:int =1,size:int =10,
                     phone:str=Form(None),name:str=Form(None),globalName:str=Form(None),
                     leadBy:int=Form(None),lead_status:int=Form(None),
                     state:str=Form(None),city:str=Form(None),
                     country:str=Form(None),
                     fromdatetime:date=Form(None),
                     todatetime:date=Form(None),
                     lead_code:str=Form(None),
                     dealerId:int=Form(None),
                     employeeId:int = Form(None)
                     ):
    user = deps.get_user_token(db=db,token=token)
    if user:

        today = datetime.now(settings.tz_IN)
        todayDt =  datetime.now()

        if fromdatetime:
            fromdatetime = fromdatetime.strftime("%Y-%m-%d 00:00:00")
        else:
            fromdatetime = today.replace(day=1,month=1).strftime("%Y-%m-%d 00:00:00")
        if not todatetime:
            todatetime = today.replace(day=31,month=12).strftime("%Y-%m-%d 23:59:59")
        else:
            todatetime = todatetime.strftime("%Y-%m-%d 23:59:59")

        getAllLead = db.query(Lead).filter(Lead.status==1)

        if fromdatetime or todatetime:
            getAllLead =  getAllLead.filter(Lead.update_at.between(fromdatetime,todatetime))

            
        threshold_datetime = datetime.now(settings.tz_IN) - timedelta(hours=24)
        count = 0
        leadStatusData =[6,7,17]

        if not lead_status in [5,9]:
             getAllLead=getAllLead.filter(Lead.update_at <= threshold_datetime)
   

        getAllLead = getAllLead.filter(Lead.lead_status_id.notin_(leadStatusData))
                       
        if globalName:
            getAllLead = getAllLead.filter(or_(Lead.name.like("%"+globalName+"%"),
                                    Lead.company_name.like("%"+globalName+"%"),
                                    Lead.contact_person.like("%"+globalName+"%"),
                                    Lead.lead_code.like("%"+globalName+"%"),
                                    Lead.phone.like("%"+globalName+"%"),
                                    Lead.alternative_no.like("%"+globalName+"%"),
                                    Lead.whatsapp_no.like("%"+globalName+"%"),
                                    Lead.email.like("%"+globalName+"%"),
                                    Lead.landline_number.like("%"+globalName+"%"),

                                    ))
       
        if user.user_type == 3:
            getAllLead = getAllLead.filter(Lead.dealer_id == user.id)
        elif user.user_type == 4:
            getAllLead = getAllLead.filter(Lead.assigned_to == user.id)
     
        
        
        if phone:
            getAllLead = getAllLead.filter(Lead.phone.like("%"+phone+"%"))
        if name:
            getAllLead = getAllLead.filter(Lead.name.like("%"+name+"%"))
        if leadBy:
            getAllLead = getAllLead.filter(Lead.enquiry_type_id==leadBy)
        
        if lead_status and lead_status not in [5,9] :
            getAllLead = getAllLead.filter(Lead.lead_status_id==lead_status)
        if lead_status!=7:
            getAllLead = getAllLead.filter(Lead.lead_status_id!=7)

        if lead_status in [5,9]:
            getAllLead = getAllLead.filter(Lead.is_followup==1,(func.DATE_FORMAT(Lead.schedule_date, '%Y-%m-%d %H:%M') < today.strftime('%Y-%m-%d %H:%M')))
            # for i in getAllLead.all():
            #                 print(i.id)
        # if lead_status:
        #     getAllLead = getAllLead.filter(Lead.lead_status_id==lead_status)
        if state:
            getAllLead = getAllLead.filter(Lead.states.like("%"+state+"%"))  
        if country:
            getAllLead = getAllLead.filter(Lead.country.like("%"+country+"%"))
        if city:
            getAllLead = getAllLead.filter(Lead.city.like("%"+city+"%"))
        if lead_code:
            getAllLead = getAllLead.filter(Lead.lead_code.like("%"+lead_code+"%"))
        if dealerId:
            getAllLead = getAllLead.filter(Lead.dealer_id == dealerId)
        if employeeId:
            getAllLead = getAllLead.filter(Lead.assigned_to == employeeId)
      
        getAllLead = getAllLead.order_by(Lead.schedule_date.asc())

        totalCount = getAllLead.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllLead = getAllLead.offset(offset).limit(limit).all()

        dataList =[]
        
        if getAllLead:
            for row in getAllLead:

                files=[]
                getFiles= db.query(LeadMedia).filter(LeadMedia.lead_id==row.id,
                                                         LeadMedia.status==1).all()
                    
                for file in getFiles:
                        files.append({
                            "file_id":file.id,
                            "url":f"{settings.BASE_DOMAIN}{file.url}",
                            "lead_history_id":file.lead_history_id

                        })

                dueType=0
                missedDays=None
                remainingDays=None
                if row.schedule_date and row.is_followup==1:
                # if row.schedule_date and row.lead_status_id==5:
                    if row.schedule_date.strftime('%Y-%m-%d %H:%M')<todayDt.strftime('%Y-%m-%d %H:%M'):
                        dueType = -1
                        missedDays=(todayDt-row.schedule_date).days

                    elif row.schedule_date.strftime('%Y-%m-%d %H:%M')==todayDt.strftime('%Y-%m-%d %H:%M') or (row.schedule_date>todayDt and row.schedule_date.date()==todayDt.date()):
                        dueType = 1
                        remainingDays=0

                    elif row.schedule_date.strftime('%Y-%m-%d %H:%M')>todayDt.strftime('%Y-%m-%d %H:%M'):
                        dueType = 2    
                        remainingDays=(row.schedule_date-todayDt).days       

                getFollowUp = db.query(FollowUp).filter(FollowUp.lead_id == row.id,
                                                             FollowUp.status == 1)
                    
                    
                getFollowUp = getFollowUp.order_by(FollowUp.id.desc()).first()
                    

                dataList.append(
                    {
                         "followup_enquiry_type":getFollowUp.enquiry_type.name if getFollowUp and getFollowUp.enquiry_type_id else None,
                        "followup_enquiry_id":getFollowUp.enquiry_type_id if getFollowUp  else None,
                        "is_followup":row.is_followup,
                        "leadCode":row.lead_code,
                        "due_type":dueType,
                        "email":row.email,
                        "leadId":row.id,
                        "missed_days":missedDays,
                        "remaining_days":remainingDays,
                        "leadName":row.name,
                        "landline_number":row.landline_number,
                        "remarks":row.remarks,
                        "companyName":row.company_name,
                        "mobile":row.phone,
                        "city":row.city,
                        "state":row.states,
                        "country":row.country,
                        "area":row.area,
                        "address":row.address,
                        "pincode":row.pincode,
                        "refer_country_code":row.refer_country_code  ,
                        "whatsapp_no":row.whatsapp_no if row.whatsapp_no else None,
                        "phone_country_code":row.customer.phone_country_code if row.customer_id else None ,
                        "whatsapp_country_code":row.customer.whatsapp_country_code if row.customer_id else None,
                        "alter_country_code":row.customer.alter_country_code if row.customer_id else None,
                        "competitorName":row.competitor_name,
                        "competitor_id":row.competitor_id,
                        "dealerId":row.dealer_id,
                        "dealerName":row.dealer_user.name if row.dealer_id else None,
                        "dealerActiveStatus":row.dealer_user.is_active if row.dealer_id  else None,
                        "employee_id":row.assigned_to,
                        "employeeActiveStatus": row.assigned_user.is_active if row.assigned_to  else None,
                        "assignedTo":row.assigned_user.name if row.assigned_to else (row.dealer_user.name if row.dealer_id  and row.lead_status_id!=1 else None),
                        "receivedAt":row.received_at.strftime("%Y-%m-%d %H:%M:%S") if row.received_at else None,
                        "isActive":row.is_active,
                        "leadStatusId":row.lead_status_id,
                        "leadStatusName":row.lead_status.name if row.lead_status_id else None,
                        "leadComment":row.tempComment,
                        "schedule_date":row.schedule_date,
                        'transferComment':row.transferComment,
                        "referNumber":row.refered_ph_no,
                        "referName":row.refered_by,
                        "activeStatus":row.is_active,
                        "demo_date":row.demo_date,
                        "poc_date":row.poc_date,
                         "approximate_amount":row.approximate_amount,
                        "drop_reason":row.drop_reason,
                        "created_at":row.created_t,
                        "created_by":row.create_user.user_name if row.created_by else None,
                        "files":files,
                        "created_by_id":row.created_by,


                    }
                )
                missedDays=None
                remainingDays=None
        data=({"page":page,"size":size,
                   "total_page":totalPage,
                   "total_count":totalCount,
                   "items":dataList,
                   "attentionCount":count})
        return ({"status":1,"msg":"Success","data":data})
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/view_lead")
async def viewLead(db: Session = Depends(deps.get_db),
                   token:str = Form(...),
                   leadId:int =Form(...) ):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        getLead = db.query(Lead).filter(Lead.id == leadId,
                                        Lead.status ==1).first()
        today = datetime.now()
        
        data1 =[]
        if not getLead:
            return {"status":0,"msg":"No lead record found."}
        else:
            if getLead.requirements_id:
                getRequirementData = [int(row) for row in getLead.requirements_id.split(",")]
                getAllReq = db.query(Requirements.id,Requirements.name).filter(Requirements.id.in_(getRequirementData),Requirements.status==1).all()
                for row in getAllReq:
                    data1.append({"reqId":row.id,"reqName":row.name} ) 


            files=[]
            getFiles= db.query(LeadMedia).filter(LeadMedia.lead_id==leadId,
                                                    LeadMedia.status==1).all()
            
            for file in getFiles:
                files.append({
                    "file_id":file.id,
                    "url":f"{settings.BASE_DOMAIN}{file.url}",
                    "lead_history_id":file.lead_history_id

                })
            dueType=0
            missedDays=None
            remainingDays=None
            todayDt = datetime.now()

            if getLead.schedule_date and getLead.lead_status_id==5:
                    if getLead.schedule_date.strftime('%Y-%m-%d %H:%M')<today.strftime('%Y-%m-%d %H:%M'):
                        dueType = -1
                        missedDays=(todayDt-getLead.schedule_date).days
                    elif getLead.schedule_date.strftime('%Y-%m-%d %H:%M')==today.strftime('%Y-%m-%d %H:%M') or (getLead.schedule_date>today and getLead.schedule_date.date()==today.date()):
                        dueType = 1
                        remainingDays=0

                    elif getLead.schedule_date.strftime('%Y-%m-%d %H:%M')>today.strftime('%Y-%m-%d %H:%M'):
                        dueType = 2     
                        remainingDays=(getLead.schedule_date-todayDt).days       


            data = {
                "created_by_id":getLead.created_by,

                "is_followup":getLead.is_followup,
                "leadId":getLead.id,
                "due_type":dueType,
                'leadCode':getLead.lead_code,
                "customer_name":getLead.contact_person,
                "refer_country_code":getLead.refer_country_code  ,
                "remarks":getLead.remarks,
                "name":getLead.name,
                "missed_days":missedDays,
                "remaining_days":remainingDays,

                "landline_number":getLead.landline_number,

                "company_name":getLead.company_name,
                "userName":getLead.contact_person,
                "alternativeNumber":getLead.alternative_no,
                "whatsapp_no":getLead.whatsapp_no,
                "phone_country_code":getLead.customer.phone_country_code if getLead.customer_id else None ,
                "whatsapp_country_code":getLead.customer.whatsapp_country_code if getLead.customer_id else None,
                "alter_country_code":getLead.customer.alter_country_code if getLead.customer_id else None,
                "address":getLead.address,
                "area":getLead.area,
                "customerCategoryId":getLead.customer_category_id,
                "categoryName":getLead.customer_category.name if getLead.customer_category_id else None ,
                "enquiryTypeId":getLead.enquiry_type_id,
                "enquiryTypeName":getLead.enquiry_type.name if getLead.enquiry_type_id else None ,
                "leadStatusId":getLead.lead_status_id,
                "leadStatusName":getLead.lead_status.name if getLead.lead_status_id else None,
                "requirementsId":data1,
                "pincode":getLead.pincode,
                "phoneNumber":getLead.phone,
                "email":getLead.email,
                "stateName":getLead.states,
                "cityName":getLead.city,
                "countryName":getLead.country,

                "dealerId":getLead.dealer_id,
                "dealerName":getLead.dealer_user.name if getLead.dealer_id else None,
                "dealerActiveStatus":getLead.dealer_user.is_active if getLead.dealer_id  else None,
                "assigned_to":getLead.assigned_to,
                "assignedUserName":getLead.assigned_user.name if getLead.assigned_to else None ,
                "employeeActiveStatus": getLead.assigned_user.is_active if getLead.assigned_to  else None,
                "receivedAt":getLead.received_at,
                "referedBy":getLead.refered_by,
                "referNumber":getLead.refered_ph_no,
                "notes":getLead.notes,
                "competitor_id":getLead.competitor_id,
                "competitor_name":getLead.competitor_name,
                "description":getLead.comments_description,
                 "schedule_date":getLead.schedule_date,
                 "poc_date":getLead.poc_date,
                 "demo_date":getLead.demo_date,
                "created_at":getLead.created_t,
                "created_by":getLead.create_user.user_name if getLead and getLead.created_by else None,

                  "transferComment":getLead.transferComment,
                "approximate_amount":getLead.approximate_amount,

                   "files":files }

            return {"status":1,"msg":"success","data":data}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/changeLeadStatus")
async def changeLeadStatus(db: Session = Depends(deps.get_db),
                   token:str = Form(...),
                   leadId:int =Form(...),leadStatus:int=Form(...),
                   competitor:str=Form(None),
                   follow_up_date:datetime=Form(None),
                   poc_date:datetime=Form(None),
                   enquiry_type:int=Form(None),
                   demo_date:datetime=Form(None),
                   comment:str=Form(None),competitor_id:int=Form(None),
                   longitude:str=Form(None),latitude:str=Form(None),is_changed:int = Form(None),
                   dropReason:str=Form(None),
                   upload_file:Optional[List[UploadFile]] = File(default=None)
                   ):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        if is_changed:
            getLead = db.query(Lead).filter(Lead.id == leadId,
                                            Lead.status == 1).first()
            if not getLead:
                return {"status":0,"msg":"No lead record found."}
            else:
                getLeadStatus =  db.query(LeadStatus).filter(LeadStatus.id==leadStatus,
                                                            LeadStatus.status.in_([1,2,3])).first()
                if not getLeadStatus:
                    return {'status':0,"msg":"Invalid lead status."}
                
                if leadStatus==7 and dropReason==None :
                    return {'status':0,"msg":"Cancelling the Lead, Provide the Reason For Cancellation"}
                
                comment = comment 
                historyId = None
                followupId = None

                if poc_date:
                    getLead.poc_date=poc_date
                    comment = comment or "no reason"
                    comment = f"{comment} (The POC date is {poc_date})"
                    db.commit()
                if demo_date:
                    comment = comment or "no reason"
                    comment = f"{comment} (The Demo date is {demo_date})"

                    getLead.demo_date=demo_date
                    db.commit()


                if leadStatus==5:

                    if follow_up_date<datetime.now():
                        return{"status":0,"msg":"Only future datetime are allowed."}
                    followup_dt =follow_up_date.strftime('%Y-%m-%d %H:%M')
        

                    inCompletefollowUp = db.query(FollowUp).filter(FollowUp.status==1,
                                        FollowUp.lead_id==getLead.id,FollowUp.followup_status==1).first()
                    
                    if inCompletefollowUp:
                        inCompletefollowUp.followup_status=-1
                        # return {"status":0,"msg":"This lead already has an incomplete follow-up scheduled."}
                    
                    commentTemplate =f"{comment} (The follow-up date is scheduled for {followup_dt})"

                    if not comment:
                        commentTemplate=f"The follow-up date is scheduled for {followup_dt}"

                    getLead.schedule_date = followup_dt
                    getLead.is_followup = 1

                
                    newFollowUp = FollowUp(
                        lead_id= getLead.id,
                        followup_dt = followup_dt,
                        enquiry_type_id =enquiry_type,
                        createdBy = user.id,
                        comment = commentTemplate,
                        followup_status = 1,
                        created_at = datetime.now(settings.tz_IN),
                        status = 1 )
                    db.add(newFollowUp)
                    db.commit()
                    followupId=newFollowUp.id


                    addHistory = LeadHistory(
                        lead_id= getLead.id,
                        followup_id = newFollowUp.id,
                        enquiry_type_id =enquiry_type,
                        leadStatus = "Follow up",
                        lead_status_id =5,
                        changedBy= user.id,
                        comment = commentTemplate,
                        created_at = datetime.now(settings.tz_IN),
                        status = 1
                    )
                    db.add(addHistory)
                    db.commit()
                    historyId = addHistory.id
                    scheduler.add_job(scheduled_task, 'date', run_date=getLead.schedule_date,args=[db,getLead.id])

                    # if (not getLead.schedule_date and comment) or  (follow_up_date and not comment):
                    #     comment = comment or "no reason"
                    #     comment = f"{comment} (Schedule date is {follow_up_date.date()})" 
                    # elif getLead.schedule_date and not comment:
                    #     comment = f"Schedule Change from {getLead.schedule_date.date()} to {follow_up_date.date()} "
                    # elif getLead.schedule_date and comment:
                    #     comment = f"{comment} (Schedule Change from {getLead.schedule_date.date()} to {follow_up_date.date()}) "
                if leadStatus!=5:
                    comment= comment or "no reason"
                    createLeadHistory =  LeadHistory(
                    lead_id = leadId,
                    leadStatus = getLeadStatus.name ,
                    lead_status_id=leadStatus,
                    longitude =longitude,
                    latitude=latitude,
                    changedBy = user.id,
                    comment=comment if leadStatus!=7 else dropReason,
                    created_at = datetime.now(settings.tz_IN),
                    status=1 )
                    db.add(createLeadHistory)
                    db.commit()

                    historyId = createLeadHistory.id

                name= None
                dataId = None

                if competitor_id:
                    checkCompetitor = db.query(Competitors).filter(Competitors.id == competitor_id,
                                                                Competitors.status == 1 ).first()
                    if not checkCompetitor:
                        return {"status":0,"msg":"Competitor record not found."}
                    else:
                        if competitor_id !=1:
                            name = checkCompetitor.name
                            dataId = competitor_id

                        else:
                            dataId = competitor_id
                            name = competitor
                
                if follow_up_date and leadStatus==5:
                    getLead.schedule_date =follow_up_date
                        
                getLead.competitor_name = name
                getLead.tempComment = comment
                getLead.competitor_id = dataId
                getLead.lead_status_id = leadStatus
                getLead.drop_reason = dropReason
                getLead.update_at = datetime.now(settings.tz_IN)
                db.commit()

            if upload_file and upload_file != None:
                    
                for i in range(len(upload_file)):  
                    
                    store_fname = upload_file[i].filename
                    
                    f_name,*etn = store_fname.split(".")
                
                    file_path,file_exe = file_storage(upload_file[i],f_name)
                    add_file = LeadMedia(
                        lead_id = getLead.id,
                        url = file_exe,
                        followup_id = followupId,
                        lead_history_id = historyId,
                        created_at = datetime.now(tz=settings.tz_IN),
                        upload_by = user.id,
                        status = 1,
                    )  
                    db.add(add_file)  
                    db.commit()  

            return {"status":1,"msg":"Successfully status changed."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/changeStatusAttention")
async def changeStatusAttention(db:Session=Depends(deps.get_db),token:str=Form(None)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        # threshold_datetime = datetime.now(settings.tz_IN) - timedelta(hours=48)
        # getAllLead =  db.query(Lead).filter(Lead.status==1)
            
        # leadStatusData =[6,7,17] #6->Order 7->Close 17->Not valid

        # getAllLead = getAllLead.filter(Lead.lead_status_id.notin_(leadStatusData),
        #                     Lead.update_at <= threshold_datetime)
        
        # unassignedLeads = getAllLead.filter(Lead.assigned_to.is_(None))
        # assignedLeads = getAllLead.filter(Lead.assigned_to.isnot(None))
        
        # unassignedLeads.update({"update_at":datetime.now(settings.tz_IN),"lead_status_id":1})
        # assignedLeads.update({"update_at":datetime.now(settings.tz_IN),"lead_status_id":2})
        # db.commit()
        return {"status":1,"msg":"Success"}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/listLeadHistory")
async def listLeadHistory(db: Session = Depends(deps.get_db),
                   token:str = Form(...),page:int=1,size:int=10,
                   leadStatusId:int=Form(None),
                   leadId:int =Form(None),isDownload:int=Form(None)):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        if leadId:
            getLead = db.query(Lead).filter(Lead.id == leadId,
                                        Lead.status ==1).first()
            if not getLead:
                return {"status":0,"msg":"No lead record found."}
            else:
                getAllHistory = db.query(LeadHistory).\
                    filter(LeadHistory.lead_id == leadId,
                            LeadHistory.status ==1)
        else:
            getAllHistory = db.query(LeadHistory).\
                    filter(LeadHistory.changedBy == user.id,
                            LeadHistory.status ==1)
        if leadStatusId:
            getAllHistory = getAllHistory.filter(LeadHistory.lead_status_id==leadStatusId)

        getAllHistory = getAllHistory.order_by(LeadHistory.id.desc())
        # getAllHistory = getAllHistory.filter(LeadHistory.followup_id==None).order_by(LeadHistory.id.desc())
        
        totalCount =0  
        totalPage=0 
        if not isDownload:
            totalCount = getAllHistory.count()
            totalPage,offset,limit = get_pagination(totalCount,page,size)
            getAllHistory = getAllHistory.offset(offset).limit(limit)
            
        getAllHistory = getAllHistory.all()

        dataList =[]
        if getAllHistory:
            for row in getAllHistory:

                files=[]
                getFiles= db.query(LeadMedia).filter(LeadMedia.lead_history_id==row.id,
                                                         LeadMedia.status==1).all()
                    
                for file in getFiles:
                        files.append({
                            "file_id":file.id,
                            "url":f"{settings.BASE_DOMAIN}{file.url}",
                            "lead_history_id":file.lead_history_id
                        })
    
                dataList.append(
                    {
                        "leadHistoryId":row.id,
                        "leadStatus":row.leadStatus,
                        "changedBy":row.user.name,
                        "updated_at":row.created_at,
                        "enquiry_type_id":row.enquiry_type_id,
                        "enquire_type":row.enquiry_type.name if row.enquiry_type_id else None,
                        "longitude":row.longitude,
                        "latitude":row.latitude,
                        "comment":row.comment,
                        "date":row.created_at,
                        "led_code":row.lead.lead_code if row.lead_id else None,
                        "files":files
                    })
            
        data=({"page":page,"size":size,
                "total_page":totalPage,
                "total_count":totalCount,
                "items":dataList})
        return ({"status":1,"msg":"Success","data":data})
    
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/lead_reassign")
async def LeadReassign(db: Session = Depends(deps.get_db),
                   token:str = Form(...),employeeId:int=Form(None),
                   leadId:str =Form(...),dealerId:int=Form(None),
                   longitude:str=Form(None),
                   latitude:str=Form(None),comment:str=Form(None),is_change:int=Form(None)):
    

    user = deps.get_user_token(db=db,token=token)
    if user:
        if is_change:
            if user.user_type in [1,2,3,4]:
                userDataType =[1,2]

                leadIds = leadId.split(',')

                getLead = db.query(Lead).filter()

                leadDetails = []

                for eachLead in leadIds:
                    getLead = db.query(Lead).filter(Lead.id == eachLead,
                                                    Lead.status ==1).first()
                    if not getLead:
                        return {"status":0,"msg":"No lead record found."}
                    if getLead.lead_status_id == 17:
                        return {"status":0,"msg":"You cannot transfer this non valid lead."}
                    
                    leadDetails.append({"leadId":eachLead,
                                        "oldEmployee":getLead.assigned_user.name if getLead.assigned_user else None,
                                        "oldDealer":getLead.dealer_user.name if getLead.dealer_user else None})
                    

                transferLeads = db.query(Lead).filter(Lead.status==1,
                   Lead.id.in_(leadIds))
                
                checkDealer = None
                if dealerId:
                
                    checkDealer = db.query(User).filter(User.id == dealerId,
                                    User.user_type ==3,
                                    User.status == 1).first()
                    if not checkDealer:
                        return {"status":0,"msg":"No dealer record found."}
                    dealerId = checkDealer.id
                            
                
                checkEmployee = None
                    
                if employeeId:
                    checkEmployee = db.query(User).filter(User.id == employeeId,
                                                        User.user_type ==4,
                                                        User.status == 1).first()
                    if not checkEmployee:
                        return {"status":0,"msg":"No sales person record found."}
                
                    else:         
                        assignedUser = transferLeads.update({"assigned_to":employeeId,
                                             "lead_status_id":case((Lead.lead_status_id != 1, Lead.lead_status_id), else_=2),
                                             "update_at":datetime.now(settings.tz_IN),
                        "transferComment":comment})
                 
   
                else:
                    assignedUser = transferLeads.update({"assigned_to":None,
                                             "lead_status_id":case((Lead.lead_status_id != 1, Lead.lead_status_id), else_=2),
                                             "update_at":datetime.now(settings.tz_IN),
                        "transferComment":comment})

                    
                if user.user_type in userDataType: #Admin

                    if dealerId:
                        changeDealer = transferLeads.update({"dealer_id":dealerId,"update_at":datetime.now(settings.tz_IN),
                        "transferComment":comment, "lead_status_id":case((Lead.lead_status_id != 1, Lead.lead_status_id), else_=2)})
                    else:
                        changeDealer = transferLeads.update({"dealer_id":None,
                                                            "lead_status_id":case((Lead.lead_status_id != 1, Lead.lead_status_id), else_=2),
                                                            "update_at":datetime.now(settings.tz_IN),
                        "transferComment":comment})
                if user.user_type==3:
                    changeDealer = transferLeads.update({"dealer_id":user.id})

                db.commit()

                for eachLead in leadDetails:

                    thisLead = db.query(Lead).filter(Lead.status==1,Lead.id==eachLead["leadId"]).first()
                    oldEmployee = eachLead["oldEmployee"]           
                    oldDealer = eachLead["oldDealer"]         
                    newDealer = checkDealer.name if checkDealer else None  

                    employeeComment = comment or "no reason"
                    newUser = checkEmployee.name if checkEmployee else "-"


                    commentTemplate = None
                    # if user.user_type==3:
                    if user.user_type in [3,4]:
                        if oldEmployee and oldEmployee!=newUser:
                            commentTemplate = f"sales person change from {oldEmployee} to {newUser} because of {employeeComment}"
                        else:
                            commentTemplate = f"sales person assigned to {newUser} because of {employeeComment}"
                    if user.user_type<=2:
                        if oldDealer and oldDealer!=newDealer:
                            commentTemplate = f"Admin change Lead from {oldDealer} to {newDealer} because of {employeeComment}"
                        else:
                            commentTemplate = f"Admin assign Lead to {newDealer} because of {employeeComment}"

                    createLeadHistory =  LeadHistory(
                    lead_id = thisLead.id,
                    leadStatus = thisLead.lead_status.name ,
                    lead_status_id=thisLead.lead_status_id,
                    longitude =longitude,
                    latitude=latitude,
                    changedBy = user.id,
                    comment = commentTemplate,
                    created_at = datetime.now(settings.tz_IN),
                    status=1 )
                    db.add(createLeadHistory)
                    db.commit()
                
                userIds = []
                if dealerId:
                    userIds.append(int(dealerId))
                if employeeId:
                    userIds.append(employeeId)

                msg = {
                    "msg_title": "Maestro Sales",
                    "msg_body": "Lead has been Re assigned to you.",
                }
                # lead_id = 0

                # if len(leadIds)<=1:
                lead_id=leadId

                message_data = {"lead_id":lead_id,"id":2}

                PushNotidy = send_push_notification(
                    db, userIds, msg, message_data
            )

                return {"status":1,"msg":"Reassigning successfully completed. "}
        else:
            return {"status":1,"msg":"success."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    

@router.post("/delete_lead")
async def deleteLead(db:Session=Depends(deps.get_db),
                     token:str = Form(...),
                   leadId:int =Form(...)):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        status=-1
        if user.user_type==4:
            print("hsi")
            status=0
        getLead = db.query(Lead).filter(Lead.id == leadId,
                                        Lead.status ==1).update({"status":status,"deletedBy":user.id})
        # getLeadHistory = db.query(LeadHistory).filter(LeadHistory.lead_id == leadId).update({'status':-1})
        db.commit()

        return {"status":1,"msg":"Lead successfully deleted."}
    return {"status":-1,"msg":"Your login session expires.Please login again."}



@router.post("/hot_lead")
async def hot_lead(db:Session=Depends(deps.get_db),token:str=Form(...),leadId:int=Form(...),
                   isActive:int=Form(...,description="1->active,0->inactive")):
    user = deps.get_user_token(db=db,token=token)
    if user:
        getLead = db.query(Lead).filter(Lead.id == leadId,Lead.status == 1).first()
        if getLead:
            if isActive == 1:
                getLead.is_active = 1 
                db.commit()
                return {"status":1,"msg":"Lead successfully marked as high priority / hot lead"}
            else:
                getLead.is_active = 0
                db.commit()
                return {"status":1,"msg":"Lead successfully removed from high priority / hot lead"}
        else:
            return {"status":0,"msg":"No lead record found."}
    return {"status":-1,"msg":"Your login session expires.Please login again."}


@router.post("/followup_notify")
async def followup_notify(db:Session=Depends(deps.get_db),token:str=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        todayDt = datetime.now(settings.tz_IN)
        getLead = db.query(Lead).filter(Lead.status == 1,
                                    Lead.is_followup==1,
                                     func.cast(Lead.schedule_date,Date)==todayDt.date())

        if user.user_type==3:
            getLead = getLead.filter(Lead.dealer_id==user.id)

        if user.user_type==4:
            getLead = getLead.filter(Lead.dealer_id==user.id)

        getLead = getLead.all()

        if getLead:
           
           leadIds = [row.id for row in getLead]

           message_data = {"lead_id":leadIds,"id":2}
           
           msg="Today FollowUp"

           PushNotidy = send_push_notification(
                    db, user.id, msg, message_data
            )


           return {"status":1,"msg":"Success."}
    return {"status":-1,"msg":"Your login session expires.Please login again."}




from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()


def scheduled_task(db,lead_id):
        
        message_data = {"lead_id":lead_id,"id":2}
           
        msg = {
                    "msg_title": "Maestro Sales",
                    "msg_body": "Now you have a follow-up!",
                }

        getUserId = db.query(Lead).filter(Lead.status==1,Lead.id==lead_id).first()
        userIds=[]
        today=datetime.now()

        if getUserId.assigned_to:
            userIds.append(getUserId.assigned_to)
        if getUserId.dealer_id:
            userIds.append(getUserId.dealer_id)
        
        
        PushNotidy = send_push_notification(
                    db, userIds, msg, message_data
            )
            
            
        getSchedule = db.query(Lead).filter(Lead.status==1,Lead.is_followup==1,
                                            and_(func.cast(Lead.schedule_date,Date)==today.date(),
                                                 Lead.schedule_date<today))\
                                                .order_by(Lead.schedule_date).all()
        
        
        for lead in getSchedule:
            job_id=f"lead_{lead.id}"
            if job_id in scheduler.get_jobs():
                scheduler.remove_job(job_id)


@router.on_event("startup")
def startup_event():
    scheduler.start()
    today=datetime.now()
    db=SessionLocal()

    getSchedule = db.query(Lead).filter(Lead.status==1,Lead.is_followup==1,
                                        or_(func.cast(Lead.schedule_date,Date)==today.date(),
                                            func.cast(Lead.schedule_date,Date)>today.date())
                                        )\
                                            .order_by(Lead.schedule_date).all()
    
    # for job in scheduler.get_jobs():
    #     scheduler.remove_job(job.id)
    
    for lead in getSchedule:
        scheduler.add_job(scheduled_task, 'date', run_date=lead.schedule_date,id=f"lead_{lead.id}",args=[db,lead.id])


@router.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()
    
