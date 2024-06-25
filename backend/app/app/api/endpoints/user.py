
from fastapi import APIRouter, Depends, Form,requests
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_
from app.core import security

router = APIRouter()




@router.post("/create_user")
async def createUser(db:Session = Depends(deps.get_db),
                     token:str = Form(...),name:str = Form(...),
                     userName:str=Form(...),phoneNumber:str=Form(...),
                     email:str=Form(None),
                     landline_number:str=Form(None),
                     state:str=Form(None),city:str=Form(None),country:str=Form(None),password:str=Form(None),
                     userType:int=Form(None,description="2->Admin,3->Dealer,4->employee"),pincode:str=Form(None),
                     dealer_id : int=Form(None)
                     ):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type != 4: #Employee
            getUser = db.query(User).filter(User.status == 1,User.user_type != 5)
            password = password.strip() if password else None
             
            if deps.contains_emoji(name):
                return {"status":0,"msg":"Emojis are not allowed to use."}
            if userName:
                if deps.contains_emoji(userName):
                    return {"status":0,"msg":"Emojis are not allowed to use."}
                checkUserName = getUser.filter(or_(User.user_name == userName,User.email==userName,User.phone==userName) ).first()
                if checkUserName:
                    return {"status": 0,"msg": "Username already exists. "}
                
            if email:
                if deps.contains_emoji(email):
                    return {"status":0,"msg":"Emojis are not allowed to use in email"}
                checkEmail = getUser.filter(User.email == email ).first()
                if checkEmail:
                    return {"status":0,"msg":"Email already exists."}
            
            checkMobileNumber = getUser.filter(User.phone == phoneNumber).first()
            if checkMobileNumber:
                return {"status":0,"msg":"Mobile already in use."}

            
            if user.user_type == 3:
                userType = 4
            else:
                if not userType:
                    return {"status":0,"msg":"Need user type."}
                
            if userType == 4:
                if not dealer_id and not user.user_type == 3:
                        return {"status":0,"msg":"Need dealer."}
                elif user.user_type == 3:
                    dealer_id = user.id
                    checkDealerId = getUser.filter(User.id == dealer_id).first()
                    if not checkDealerId:
                        return {"status":1,"msg":"Invalid dealer."}

                else:
                    checkDealerId = getUser.filter(User.id == dealer_id).first()
                    if not checkDealerId:
                        return {"status":1,"msg":"Invalid dealer."}
                    else:
                        dealer_id = dealer_id
            else:
                    dealer_id =None
            
            createUsers = User(
                user_type = userType,
                name = name,
                user_name = userName,
                email = email,
                phone = phoneNumber,
                states = state,
                city = city,
                landline_number = landline_number,
                country = country,
                pincode = pincode,
                password =  get_password_hash(password) if password !=None else None,
                dealer_id = dealer_id,
                is_active = 1,
                created_at = datetime.now(settings.tz_IN),
                updated_at = datetime.now(settings.tz_IN),
                status =1)
            
            db.add(createUsers)
            db.commit()

            return {"status":1,"msg":"User created successfully."}
        else:
            return {'status':0,"msg":"You are not authenticated to create a user."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/update_user")
async def updateUser (db:Session=Depends(deps.get_db),
                      token:str=Form(...),name:str = Form(...),
                     userName:str=Form(None),phoneNumber:str=Form(...),
                     state:str=Form(None),city:str=Form(None),country:str=Form(None),
                     email:str=Form(None),
                     landline_number:str=Form(None),
                     userType:int=Form(None,description="2->Dealer,3->Employee"),pincode:str=Form(None),
                     dealer_id : int=Form(None),userId:int=Form(...)):
    
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type !=4:
            if deps.contains_emoji(userName):
                return {"status":0,"msg":"Emojis are not allowed to use."}
            if email:
                if deps.contains_emoji(email):
                    return {"status":0,"msg":"Emojis are not allowed to use in email."}
            if deps.contains_emoji(name):
                return {"status":0,"msg":"Emojis are not allowed to use in email."}
            
            getUser = db.query(User).filter(User.status ==1)
            checkUserId = getUser.filter(User.id == userId,User.user_type!=1).first()
            ExceptUser = getUser.filter(User.id != userId,User.user_type !=5)
            
            if checkUserId:
                if userName:
                    checkUserName = ExceptUser.filter(or_(User.user_name == userName,User.email==userName,User.phone==userName) ).first()
                    if checkUserName:
                        return {"status": 0,"msg": "Username already exists. "}
                    
                if email:
                    checkEmail = ExceptUser.filter(User.email == email ).first()
                    if checkEmail:
                        return {"status":0,"msg":"Email already exists."}
                
                checkMobileNumber = ExceptUser.filter(User.phone == phoneNumber).first()
                if checkMobileNumber:
                    return {"status":0,"msg":"Mobile already in use."}
                
                    
                if user.user_type == 3:
                    userType = 4
                else:
                    if not userType:
                        return {"status":0,"msg":"Need user type."}
                
                
                if userType == 4:
                    if not dealer_id and not user.user_type == 3:
                        return {"status":0,"msg":"Need dealer."}
                    elif user.user_type == 3:
                        dealer_id = user.id
                        checkDealerId = getUser.filter(User.id == dealer_id).first()
                        if not checkDealerId:
                            return {"status":1,"msg":"Invalid dealer."}
                        dealer_id = dealer_id

                    else:
                        checkDealerId = getUser.filter(User.id == dealer_id).first()
                        if not checkDealerId:
                            return {"status":1,"msg":"Invalid dealer."}
                        else:
                            dealer_id = dealer_id
                else:
                    dealer_id =None
                
                
                checkUserId.user_type = userType
                checkUserId.name = name
                checkUserId.user_name = userName
                checkUserId.email = email
                checkUserId.phone = phoneNumber
                checkUserId.states = state
                checkUserId.landline_number = landline_number
                checkUserId.city = city
                checkUserId.country = country
                checkUserId.pincode = pincode
                checkUserId.dealer_id = dealer_id
                checkUserId.updated_at = datetime.now(settings.tz_IN)
                
                db.commit()

                return {"status":1,"msg":"User successfully updated."}
            else:
                return {"status":0,"msg":"Invalid user."}
        else:
            return {"status":0,"msg":"You are not authenticated to modify any users."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/list_users")
async def listUser(db:Session =Depends(deps.get_db),
                   token:str=Form(...),page:int=1,
                   size:int=10,phoneNumber:str=Form(None),
                   type:int=Form(...,description="2->Admin,3->Dealer->4->Employee"),
                   email:str=Form(None),dealerId:int=Form(None),
                   username:str=Form(None)
                   ):
    user = deps.get_user_token(db=db,token=token)

    if user:
        if user.user_type !=4:
            userTypeData = [1,5,user.user_type]
            
            
            getAllUser = db.query(User).filter(User.user_type == type,User.status==1)
            
            # getAllUser = db.query(User).filter(User.status==1,User.user_type.notin_(userTypeData))
            if user.user_type == 2:
                getAllUser = getAllUser.filter(User.user_type!=2)

            elif user.user_type == 3:
                getAllUser = getAllUser.filter(User.dealer_id == user.id,
                                               User.user_type !=3)
            if phoneNumber:
                getAllUser = getAllUser.filter(User.phone.like("%"+phoneNumber+"%") )
            if email:
                getAllUser = getAllUser.filter(User.email == email)

            if dealerId:
                getAllUser = getAllUser.filter(User.dealer_id == dealerId)
            if username:
                getAllUser = getAllUser.filter(User.name.like("%"+username+"%"))
            
            getAllUser = getAllUser.order_by(User.name.asc())
            
            userCount = getAllUser.count()
            totalPages,offset,limit = get_pagination(userCount,page,size)
            getAllUser = getAllUser.limit(limit).offset(offset).all()
            
            userTypeData = ["-","-","Admin","Dealer","Employee","Customer"]
            dataList = []
            if getAllUser:
                for userData in getAllUser:
                    dataList.append(
                        {
                            "userId":userData.id,
                            "userName":userData.user_name,
                            "name":userData.name,
                            "landline_number":userData.landline_number,
                            "phoneNumber":userData.phone,
                            "whatsapp_no":userData.whatsapp_no if userData.whatsapp_no else None,
                            "email":userData.email,
                            "userStatus":userData.is_active,
                            "userType":userData.user_type,
                            "userTypeName": userTypeData[userData.user_type],
                            "dealer_id":userData.dealer_id ,
                            "dealerName":userData.dealer.user_name if userData.dealer_id else None,
                            "location":userData.city
                        }
                    )
            data=({"page":page,"size":size,
                    "total_page":totalPages,
                    "total_count":userCount,
                    "items":dataList})
            
            return ({"status":1,"msg":"Success.","data":data})
        else:
            return {"status":0,"msg":"You are not authenticated to see the user details."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/view_user")
async def viewUser(db:Session=Depends(deps.get_db),
                   token:str=Form(...),
                   userId:int=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type !=4:
            getUser = db.query(User).filter(User.id == userId,
                                            User.status == 1)
            if user.user_type ==3:
                getUser = getUser.filter(User.dealer_id == user.id)
            getUser = getUser.first()
            userTypeData = ["-","Super Admin","Admin","Dealer","Employee"]
            if getUser:
                data ={
                    "userId":userId,
                    "name":getUser.name,
                    "userName":getUser.user_name,
                    "userType":getUser.user_type,
                    "userTypeName":userTypeData[getUser.user_type],
                    "active_status":getUser.is_active,
                    "email" : getUser.email,
                    "phoneNumber": getUser.phone,
                    "whatsapp_no":getUser.whatsapp_no if getUser.whatsapp_no else None,

                    "stateName":getUser.states,
                    "cityName":getUser.city,
                    "countryName":getUser.country,
                    "pincode":getUser.pincode,
                    "dealerId":getUser.dealer_id,
                    "dealerName":getUser.dealer.user_name if getUser.dealer_id else None


                }
            return {"status":1,"msg":"Success.","data":data}
        else:
            return {'status':0,"msg":"You are not authenticated to view any user."}
    return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/delete_user")
async def deleteUser(db:Session=Depends(deps.get_db),
                     token:str = Form(...),
                     userId:int=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if userId==91:
            return {"status":0,"msg":"Do not delete this dealer as it is restricted"}
        
        if user.user_type !=4 and user.user_type!=2 :
            getUser = db.query(User).filter(User.id == userId,
                                            User.status == 1)
            if user.user_type ==3:
                getUser = getUser.filter(User.dealer_id == user.id)
            getUser = getUser.update({"status":-1,"is_active":-1})
            db.commit()
            return {"status":1,"msg":"User successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete any user"}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login again."}

@router.post("active_inactive_user")
async def activeInactiveUser(db:Session=Depends(deps.get_db),
                             token:str=Form(...),userId:int=Form(...),
                             activeStatus:int=Form(...,description="1->active,2->inactive")):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type !=4:
            getUser = db.query(User).filter(User.id == userId,
                                            User.status == 1)
            if user.user_type ==3:
                getUser = getUser.filter(User.dealer_id == user.id)
            getUser = getUser.update({"is_active":activeStatus})
            db.commit()
            message ="Success."
            if activeStatus ==1:
                message ="User successfully activated."
            else:
                message ="User successfully deactivated."

            return {"status":1,"msg":message}
        else:
            return {'status':0,"msg":"You are not authenticated to change status of any user"}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/getDealerId")
async def getDealerId(db:Session=Depends(deps.get_db),
                      token:str=Form(...),
                      user_id:int=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        getUser = db.query(User).filter(User.id == user_id,User.status ==1).first() 
        if getUser.user_type ==3:
            dealerId = getUser.dealer_id
            dealerName = getUser.dealer.user_name
        else:
            dealerId = user_id
            dealerName = getUser.dealer.user_name
        data={"dealerId":dealerId,
              "dealerName":dealerName}
        return {"status":1,"msg":"Success","data":data}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login again."}

@router.post("/get_customer_details")
async def getCustomerDetails(db:Session=Depends(deps.get_db),
                             token:str=Form(...),
                             country_code:str=Form(None),
                             customerId:int=Form(None),
                             phoneNo:int=Form(None),
                             landline_number:str=Form(None)):


    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type !=5:
            getUser = db.query(User).filter(
                                            User.user_type == 5,
                                            User.status == 1)
            
            if customerId:
                getUser =getUser.filter(User.id==customerId)

            if landline_number:
                getUser =getUser.filter(User.landline_number==landline_number)
            
            if phoneNo:
                getUser = getUser.filter(or_(and_(User.whatsapp_no==phoneNo,User.whatsapp_country_code==country_code),
                                             and_(User.alternative_number==phoneNo,User.phone_country_code==country_code),
                                             and_(User.phone==phoneNo,User.alter_country_code==country_code)))
            
            data={}
            getUser = getUser.first()
            # print(getUser)
            if getUser:
                data ={
                    "customerId":getUser.id,
                    "name":getUser.name,
                    "landline_number":getUser.landline_number,
                    "userName":getUser.user_name,
                    "userType":getUser.user_type,
                    # "userTypeName":userTypeData[getUser.user_type],
                    "email" : getUser.email,
                    "phoneNumber": getUser.phone,
                    "phone_country_code": getUser.phone_country_code,
                    "whatsapp_country_code": getUser.whatsapp_country_code,
                    "alter_country_code": getUser.alter_country_code,
                    "whatsapp_no":getUser.whatsapp_no if getUser.whatsapp_no else None,
                    "alternativeNumber":getUser.alternative_number,
                    "stateName":getUser.states,
                    "cityName":getUser.city,
                    "countryName":getUser.country,
                    "pincode":getUser.pincode,
                    "company_name":getUser.company_name,
                    "address":getUser.address,
                    "area":getUser.area,
                    "pincode":getUser.pincode 

                }
                return {"status":1,"msg":"Success.","data":data}
            return {"status":0,"msg":"No data"}
            
        else:
            return {'status':0,"msg":"You are not authenticated to view any customers."}
    return {"status":-1,"msg":"Your login session expires.Please login again."}


@router.post("/create_customer")
async def createCustomer(db:Session =Depends(deps.get_db),
                         token:str=Form(...),name:str=Form(...),
                         contact_person:str=Form(...),
                          phone_country_code:str=Form(...),
                        whatsapp_country_code:str=Form(None),
                        alter_country_code:str=Form(None),
                         phone:str=Form(...),
                         alternative_no:str=Form(None),
                         landline_number:str=Form(None),
                         whatsapp_no:str=Form(None),
                        address:str=Form(...),
                          area :str=Form(None),
                          email:str=Form(None),
                          companyName:str=Form(None),
                          pincode:str=Form(None),state:str = Form(None),
                          city:str=Form(None),district:str = Form(None)):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getUser = db.query(User).filter(User.user_type == 5,User.status == 1)
            if email:
                checkEmail = getUser.filter(User.email == email ).first()
                if checkEmail:
                    return {"status":0,"msg":"Email already exists."}
            checkMobileNumber = getUser.filter(or_(User.phone == phone,
                                                   User.alternative_number == phone,
                                                   User.whatsapp_no == phone)).first()
            if checkMobileNumber:
                return {"status":0,"msg":"Mobile number already in use."}
            if alternative_no:
                checkAlternativeMobile = getUser.filter(or_(User.phone == alternative_no,
                                                   User.alternative_number == alternative_no,
                                                   User.whatsapp_no == alternative_no)).first()
                if checkAlternativeMobile:
                    return {"status":0,"msg":"Mobile number already in use."}
            if whatsapp_no:
                checkWhatsApp = getUser.filter(or_(User.phone == whatsapp_no,
                                                   User.alternative_number == whatsapp_no,
                                                   User.whatsapp_no == whatsapp_no)).first()
                if checkWhatsApp:
                    return {"status":0,"msg":"Mobile number already in use."}

            
            createNewCustomer = User(
                user_type = 5,
                name = name,
                user_name = contact_person,
                phone = phone,
                alternative_number = alternative_no,
                phone_country_code =phone_country_code,
                whatsapp_country_code =whatsapp_country_code,
                alter_country_code =alter_country_code,
                whatsapp_no = whatsapp_no,
                landline_number = landline_number,
                address = address,
                area = area,
                states = state,
                city = city,
                pincode = pincode,
                created_at = datetime.now(settings.tz_IN),
                status = 1,
                email = email,
                company_name=companyName,
                is_active = 1
            )

            db.add(createNewCustomer)
            db.commit()
            return {"status":1,"msg":"Customer successfully created."}
        else:
            return {"status":0,"msg":"You are not authenticate to add any customer."}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login again."}

@router.post("/update_customer")
async def updateCustomer(db: Session = Depends(deps.get_db),
                         token:str=Form(...),name:str=Form(...),
                         contact_person:str=Form(...),
                         phone:str=Form(...),
                          phone_country_code:str=Form(...),
                        whatsapp_country_code:str=Form(None),
                        alter_country_code:str=Form(None),
                         alternative_no:str=Form(None),
                         whatsapp_no:str=Form(None),
                         address:str=Form(...),
                          area :str=Form(None),
                          email:str=Form(None),
                          companyName:str=Form(None),
                          pincode:str=Form(None),state:str = Form(None),
                          country:str = Form(None),
                          city:str=Form(None),CustomerId:int=Form(...)
                         ):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getUser = db.query(User).filter(User.user_type ==5,User.status == 1)
            checkUserId = getUser.filter(User.id == CustomerId).first()
            exceptionCustomer = getUser.filter(User.id != CustomerId)

            if not checkUserId:
                return {'status':0,"msg":"No customer record found."}
            if email:
                checkEmail = exceptionCustomer.filter(User.email == email ).first()
                if checkEmail:
                    return {"status":0,"msg":"Email already exists."}
            checkMobileNumber = exceptionCustomer.filter(or_(User.phone == phone,
                                                   User.alternative_number == phone,
                                                   User.whatsapp_no == phone)).first()
            if checkMobileNumber:
                return {"status":0,"msg":"Mobile number already in use."}
            if alternative_no:
                checkAlternativeMobile = exceptionCustomer.filter(or_(User.phone == alternative_no,
                                                   User.alternative_number == alternative_no,
                                                   User.whatsapp_no == alternative_no)).first()
                if checkAlternativeMobile:
                    return {"status":0,"msg":"Mobile number already in use."}
            if whatsapp_no:
                checkWhatsApp = exceptionCustomer.filter(or_(User.phone == whatsapp_no,
                                                   User.alternative_number == whatsapp_no,
                                                   User.whatsapp_no == whatsapp_no)).first()
                if checkWhatsApp:
                    return {"status":0,"msg":"Mobile number already in use."}
                
            
            checkUserId.name = name
            checkUserId.user_name = contact_person
            checkUserId.phone = phone
            checkUserId.alternative_number = alternative_no
            checkUserId.phone_country_code = phone_country_code
            checkUserId.whatsapp_country_code = whatsapp_country_code
            checkUserId.alter_country_code = alter_country_code
            checkUserId.whatsapp_no = whatsapp_no
            checkUserId.address = address
            checkUserId.area = area
            checkUserId.states = state
            checkUserId.city = city
            checkUserId.country = country
            checkUserId.pincode = pincode
            checkUserId.updated_at = datetime.now(settings.tz_IN)
            checkUserId.email = email
            checkUserId.company_name = companyName
            
            db.commit()
            return {"status":1,"msg":"Customer details updated successfully."}
        else:
            return {"status":0,"msg":"You are not authenticated to update/edit customer details."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}


@router.post("/list_customer")
async def listCustomers(db:Session =Depends(deps.get_db),
                        token:str=Form(...),
                        page:int=1,size:int=10,
                        mobileNumber:str=Form(None),
                        name:str=Form(None),state:str = Form(None),
                          country:str = Form(None),
                          city:str=Form(None),):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllCustomer = db.query(User).filter(User.user_type == 5,
                                                   User.status == 1)
            if mobileNumber:
                getAllCustomer = getAllCustomer.\
                    filter(or_(User.phone.like('%'+mobileNumber+'%'),
                               User.alternative_number.like('%'+mobileNumber+'%'),
                               User.whatsapp_no.like('%'+mobileNumber+'%')))
            if name:
                getAllCustomer = getAllCustomer.filter(or_(User.name.like('%'+name+'%'),
                                                           User.user_name.like("%"+name+"%")))
            if state:
                getAllCustomer = getAllCustomer.filter(User.states.like("%"+state+"%"))  
            if country:
                getAllCustomer = getAllCustomer.filter(User.country.like("%"+country+"%"))
            if city:
                getAllCustomer = getAllCustomer.filter(User.city.like("%"+city+"%"))
            
            getAllCustomer = getAllCustomer.order_by(User.name.asc())
            
            totalCount = getAllCustomer.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllCustomer = getAllCustomer.limit(limit).offset(offset).all()
            dataList = []
            if getAllCustomer:
                for row in getAllCustomer:
                    dataList.append({"customerId":row.id,
                                     "name":row.name,
                                     "contactPerson":row.user_name,
                                     "phone":row.phone,
                                     "alternative_number":row.alternative_number,
                                     "phone_country_code" : row.phone_country_code,
                                    "whatsapp_country_code" :row.whatsapp_country_code,
                                    "alter_country_code" : row.alter_country_code,
                                     "address":row.address,
                                     "area":row.area,
                                    "whatsapp_no":row.whatsapp_no if row.whatsapp_no else None,

                                    "stateName":row.states,
                                    "cityName":row.city,
                                    "countryName":row.country,
                                    "pincode":row.pincode,
                                    "email":row.email,
                                    "companyName":row.company_name
                                     })
            data=({"page":page,"size":size,
                "total_page":totalPages,
                "total_count":totalCount,
                "items":dataList})
            
            return ({"status":1,"msg":"Success.","data":data})
        else:
            return {"status":0,"msg":"You are not authenticated to see the customer details."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
    
@router.post("/delete_customer")
async def deleteCustomer(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         customerId:int=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type == 1:
            deleteCustomer = db.query(User).\
                filter(User.id == customerId,
                User.user_type == 5).update({"status":-1,"is_active":-1})
            db.commit()

            return {"status":1,"msg":"Customer details successfully removed."}
        else:
            return {"status":0,"msg":"You are not authenticated to delete the customer record."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}
