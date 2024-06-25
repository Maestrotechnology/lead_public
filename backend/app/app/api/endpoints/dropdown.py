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

import random


router = APIRouter()

@router.post("/dropdown_country")
async def dropDownCustomer(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllCountry = db.query(Country.name,Country.country_code,Country.iso,Country.mobile_no_length).filter(
                                           Country.status == 1).order_by(Country.id.asc()).all()
        dataList =[]
        if getAllCountry:
            for rowName,rowCode,rowIso,noLength in getAllCountry:
                dataList.append({
                    "country_name":rowName,
                    "country_code":rowCode,
                    "country_iso":rowIso,
                    "number_length":noLength if noLength else "10"})
                
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    
@router.post("/userDropdown")
async def userDropdown(db:Session=Depends(deps.get_db),
                       token:str=Form(...),
                       isDealer:int=Form(None,description="1->dealer"),
                       isActive:int=Form(None,description="1-"),
                       dealerId:int=Form(None),is_report:int=Form(None)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        if user.user_type in [1,2,3,4]:
           
            getUser = db.query(User).filter(User.is_active!=0)
            if is_report:
                getUser = getUser
            else:
                getUser = getUser.filter(User.status == 1)
            if user.user_type == 3 :
                getUser = getUser.filter(User.dealer_id == user.id)

            if user.user_type==4:
                getUser = getUser.filter(User.dealer_id == user.dealer_id)

            if isDealer and user.user_type!=3:
                getUser = getUser.filter(User.user_type == 3)

            else:
                getUser = getUser.filter(User.user_type == 4)

            if dealerId :
                getUser = getUser.filter(User.dealer_id == dealerId)
            
            getUser = getUser.order_by(User.name.asc()).all()

            dataList =[]

            if getUser:
                for userData in getUser:
                    if userData.name=="Maestro":
                        isActive =1
                        dataList.append({
                        "userId":userData.id,
                        "userName":f"{userData.name} ({userData.phone})",
                        "isActive":1
                    })
                        continue
                    dataList.append({
                        "userId":userData.id,
                        "userName":f"{userData.name} ({userData.phone})"
                    })
            return {"status":1,"msg":"Success","data":dataList}
        else:
            return {"status":0,"msg":"You are not authenticated to see the employee details."}
    return {'status':-1,"msg":"Your login session expires.Please login later."}

@router.post("/employeeDropDown")
async def employeeDropDown(db:Session=Depends(deps.get_db),
                       token:str=Form(...),
                       dealerId:int=Form(None),is_report:int=Form(None)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        if user.user_type in [1,2,3]:
           
            getUser = db.query(User).filter(User.user_type == 4,User.is_active!=0)
            if is_report:
                getUser = getUser
            else:
                getUser = getUser.filter(User.status == 1,User.is_active == 1)
            if user.user_type == 3 :
                getUser = getUser.filter(User.dealer_id == user.id)

            if dealerId:
                getUser = getUser.filter(User.dealer_id == dealerId)
            
            count = getUser.count()
            getUser = getUser.order_by(User.name.asc()).all()

            dataList =[]

            if getUser:
                for userData in getUser:
                    dataList.append({
                        "userId":userData.id,
                        "userName":f"{userData.name}({userData.phone})"
                    })
            return {"status":1,"msg":"Success","data":dataList,"count ":count}
        else:
            return {"status":0,"msg":"You are not authenticated to see the employee details."}
    return {'status':-1,"msg":"Your login session expires.Please login later."}


@router.post("/dropdown_industry")
async def industryDropDown(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    
    user = deps.get_user_token(db=db,token =token)
    if user:
        if user.user_type in [1,2,3]:
            getAllIndustry = db.query(Industry.id,Industry.name)\
                .filter(Industry.status==1).order_by(Industry.name).Iall()
            dataList = []
            if getAllIndustry:
                for rowId,rowName in getAllIndustry:
                    dataList.append({
                        "industryId":rowId,
                        "industryName":rowName
                    }) 
            return {"status":1,"msg":"Success","data":dataList}
        else:
            return {"status":0,"msg":"You are not authenticated to see the industry details."}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    
@router.post("/dropdownCustomerCategory")
async def dropdownCustomerCategory(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllCategory = db.query(CustomerCategory.id,
                                  CustomerCategory.name).\
        filter(CustomerCategory.status==1).order_by(CustomerCategory.name.asc()).all()
        dataList = []
        if getAllCategory:
            for rowId,rowName in getAllCategory:
                dataList.append({
                    "categoryId":rowId,
                    "categoryName":rowName
                })
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    
@router.post("/dropdownEnquiry")
async def dropdownEnquiry(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllEnquiryType = db.query(EnquiryType.id,
                                  EnquiryType.name).\
        filter(EnquiryType.status==1).order_by(EnquiryType.name.asc()).all()
        dataList = []
        if getAllEnquiryType:
            for rowId,rowName in getAllEnquiryType:
                dataList.append({
                    "enquiryId":rowId,
                    "enquiryName":rowName
                })
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
        

@router.post("/dropdownRequirements")
async def dropdownRequirements(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllRequirements = db.query(Requirements.id,
                                  Requirements.name).\
        filter(Requirements.status==1).order_by(Requirements.name.asc()).all()
        dataList = []
        if getAllRequirements:
            for rowId,rowName in getAllRequirements:
                dataList.append({
                    "RequirementsId":rowId,
                    "RequirementsName":rowName
                })
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}

@router.post("/dropdownLead")
async def dropdownLead(db:Session = Depends(deps.get_db),
                           token:str=Form(...),is_all:int=Form(None)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllLead = db.query(LeadStatus.id,
                                  LeadStatus.name)
        if is_all:
            getAllLead = getAllLead
        else:
            getAllLead = getAllLead.filter(LeadStatus.status.in_([1,2]))
        
        getAllLead = getAllLead.order_by(LeadStatus.name.asc()).all()
        dataList = []
        if getAllLead:
            for rowId,rowName in getAllLead:
                dataList.append({
                    "leadStatusId":rowId,
                    "leadStatusName":rowName
                })
            dataList.append({
                    "leadStatusId":9,
                    "leadStatusName":"Missed"
                })
            
        # print(dataList,is_all)
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    
@router.post("/dropdownCompetitor")
async def dropdownLead(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllCompetitor = db.query(Competitors.id,
                                  Competitors.name).\
        filter(Competitors.status==1).order_by(Competitors.name.asc()).all()
        dataList = []
        if getAllCompetitor:
            for rowId,rowName in getAllCompetitor:
                dataList.append({
                    "competitorId":rowId,
                    "competitorName":rowName
                })
            
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    
@router.post("/dropdown_customer")
async def dropDownCustomer(db:Session = Depends(deps.get_db),
                           token:str=Form(...)):
    user = deps.get_user_token(db=db,token =token)
    if user:
        getAllUser = db.query(User.id,User.name,User.phone).filter(User.user_type == 5,
                                           User.status == 1,User.is_active==1).order_by(User.name.asc()).all()
        dataList =[]
        if getAllUser:
            for rowId,rowName,rowNumber in getAllUser:
                dataList.append({
                    "userId":rowId,
                    "userName":f"{rowName} ({rowNumber})"})
                
        return {"status":1,"msg":"Success","data":dataList}
    else:
        return {'status':-1,"msg":"Your login session expires.Please login later."}
    