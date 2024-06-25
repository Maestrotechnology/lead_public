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

#Customer category

@router.post("/create_category")
async def createCategory(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            checkName = db.query(CustomerCategory).\
                filter(CustomerCategory.name ==name ,
                       CustomerCategory.status ==1).first()
            if checkName:
                return {"status":0,"msg":"Customer category already exists."}
            else:
                newCategory = CustomerCategory(
                    name=name,
                    created_by = user.id,
                    created_at = datetime.now(settings.tz_IN),
                    updated_at = datetime.now(settings.tz_IN),
                    status = 1
                )
                db.add(newCategory)
                db.commit()
                return {"status":1,'msg':"Customer category successfully created."}
        else:
            return {'status':0,"msg":"You are not authenticated to create category."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/update_category")
async def updateCategory(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         dataId :int=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getCategory = db.query(CustomerCategory).filter(CustomerCategory.status==1)
            checkId = getCategory.filter(CustomerCategory.id == dataId).first()
            if checkId:
                checkName = getCategory.filter(CustomerCategory.name==name,
                                               CustomerCategory.id != dataId).first()
                if checkName:
                    return {"status":0,"msg":"Customer category already exists."}
                else:
                    checkId.name = name
                    checkId.created_by = user.id
                    checkId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()
                    return {"status":1,"msg":"Customer category successfully updated."}
            else:
                return {"status":1,"msg":"Invalid category."}
        else:
            return {'status':0,"msg":"You are not authenticated to update category."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/list_category")
async def listCategory(db:Session =Depends(deps.get_db),
                       token:str = Form(...),
                       page:int=1,size:int = 10,
                       name:str = Form(None)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllCategory = db.query(CustomerCategory).filter(CustomerCategory.status ==1)
            if name:
                getAllCategory = getAllCategory.filter(CustomerCategory.name.like("%"+name+"%"))
            getAllCategory = getAllCategory.order_by(CustomerCategory.name.asc())

            totalCount = getAllCategory.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllCategory = getAllCategory.limit(limit).offset(offset).all()

            dataList=[]
            if getAllCategory:
                for row in getAllCategory:
                    dataList.append(
                        {
                            "customerCategoryId":row.id,
                            "customerCategoryName":row.name,
                            "createdBy":row.user.user_name,
                            "createdAt":row.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
            
            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
        
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to view category."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


@router.post("/delete_customer_category")
async def deleteCustomerCategory(db:Session =Depends(deps.get_db),
                                 token:str = Form(...),dataId:int=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type == 1:
            return {"status":0,"msg":"Deleting this category is restricted"}

            deleteData = db.query(CustomerCategory)\
                .filter(CustomerCategory.id == dataId,CustomerCategory.status ==1 ).update({"status":-1})
            db.commit()
            return {'status':1,"msg":"Customer category successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete category."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


#Enquires

@router.post("/create_enquiry")
async def createEnquiry(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            checkName = db.query(EnquiryType).\
                filter(EnquiryType.name ==name ,
                       EnquiryType.status ==1).first()
            if checkName:
                return {"status":0,"msg":"Enquiry type already exists."}
            else:
                Newtype = EnquiryType(
                    name=name,
                    created_by = user.id,
                    created_at = datetime.now(settings.tz_IN),
                    updated_at = datetime.now(settings.tz_IN),
                    status = 1
                )
                db.add(Newtype)
                db.commit()
                return {"status":1,'msg':"Enquire type successfully created."}
        else:
            return {'status':0,"msg":"You are not authenticated to create enquire type."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/update_Enquiry")
async def updateEnquiryType(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         dataId :int=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getEnquiry = db.query(EnquiryType).filter(EnquiryType.status==1)
            checkId = getEnquiry.filter(EnquiryType.id == dataId).first()
            if checkId:
                checkName = getEnquiry.filter(EnquiryType.name==name,
                                               EnquiryType.id != dataId).first()
                if checkName:
                    return {"status":0,"msg":"Enquiry type already exists."}
                else:
                    checkId.name = name
                    checkId.created_by = user.id
                    checkId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()
                    return {"status":1,"msg":"Enquiry type successfully updated."}
            else:
                return {"status":0,"msg":"Invalid Enquiry type."}
        else:
            return {'status':0,"msg":"You are not authenticated to update Enquiry type."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/list_enquiry_type")
async def listEnquiryType(db:Session =Depends(deps.get_db),
                       token:str = Form(...),
                       page:int=1,size:int = 10,
                       name:str = Form(None)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllEnquiryType = db.query(EnquiryType).filter(EnquiryType.status ==1)
            if name:
                getAllEnquiryType = getAllEnquiryType.filter(EnquiryType.name.like("%"+name+"%"))
            getAllEnquiryType = getAllEnquiryType.order_by(EnquiryType.name.asc())

            totalCount = getAllEnquiryType.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllEnquiryType = getAllEnquiryType.limit(limit).offset(offset).all()

            dataList=[]
            if getAllEnquiryType:
                for row in getAllEnquiryType:
                    dataList.append(
                        {
                            "enquireId":row.id,
                            "enquireTypeName":row.name,
                            "createdBy":row.user.user_name if row.user else None,
                            "createdAt":row.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
            
            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
        
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to view enquire type."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


@router.post("/delete_enquire_type")
async def deleteEnquiryType(db:Session =Depends(deps.get_db),
                                 token:str = Form(...),dataId:int=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type == 1:
            return {"status":0,"msg":"Deleting this enquiry type is restricted"}

            deleteData = db.query(EnquiryType)\
                .filter(EnquiryType.id == dataId,EnquiryType.status ==1 ).update({"status":-1})
            db.commit()
            return {'status':1,"msg":"Enquiry type successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete enquiry type."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})
    

#Requirements
@router.post("/create_requirement")
async def createRequirement(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            checkName = db.query(Requirements).\
                filter(Requirements.name ==name ,
                       Requirements.status ==1).first()
            if checkName:
                return {"status":0,"msg":"Requirements already exists."}
            else:
                Newtype = Requirements(
                    name=name,
                    created_by = user.id,
                    created_at = datetime.now(settings.tz_IN),
                    updated_at = datetime.now(settings.tz_IN),
                    status = 1
                )
                db.add(Newtype)
                db.commit()
                return {"status":1,'msg':"Requirements successfully created."}
        else:
            return {'status':0,"msg":"You are not authenticated to create Requirements."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/update_requirements")
async def updateRequirements(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         dataId :int=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getRequirements = db.query(Requirements).filter(Requirements.status==1)
            checkId = getRequirements.filter(Requirements.id == dataId).first()
            if checkId:
                checkName = getRequirements.filter(Requirements.name==name,
                                               Requirements.id != dataId).first()
                if checkName:
                    return {"status":0,"msg":"Requirements already exists."}
                else:
                    checkId.name = name
                    checkId.created_by = user.id
                    checkId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()
                    return {"status":1,"msg":"Requirements successfully updated."}
            else:
                return {"status":0,"msg":"Invalid requirements."}
        else:
            return {'status':0,"msg":"You are not authenticated to update requirements."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/list_requirements")
async def listRequirements(db:Session =Depends(deps.get_db),
                       token:str = Form(...),
                       page:int=1,size:int = 10,
                       name:str = Form(None)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllRequirements = db.query(Requirements).filter(Requirements.status ==1)
            if name:
                getAllRequirements = getAllRequirements.filter(Requirements.name.like("%"+name+"%"))
            getAllRequirements = getAllRequirements.order_by(Requirements.name.asc())

            totalCount = getAllRequirements.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllRequirements = getAllRequirements.limit(limit).offset(offset).all()

            dataList=[]
            if getAllRequirements:
                for row in getAllRequirements:
                    dataList.append(
                        {
                            "RequirementsId":row.id,
                            "RequirementsName":row.name,
                            "createdBy":row.user.user_name if row.user else None,
                            "createdAt":row.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
            
            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
        
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to view requirements."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


@router.post("/delete_requirements")
async def deleteRequirements(db:Session =Depends(deps.get_db),
                                 token:str = Form(...),dataId:int=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type == 1:
            return {"status":0,"msg":"Deleting this requiremnet is restricted"}

            deleteData = db.query(Requirements)\
                .filter(Requirements.id == dataId,Requirements.status ==1 ).update({"status":-1})
            db.commit()
            return {'status':1,"msg":"Requirements successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete requirements."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

#lead_status
@router.post("/create_lead_status")
async def createLeadStatus(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            checkName = db.query(LeadStatus).\
                filter(LeadStatus.name ==name ,
                       LeadStatus.status ==1).first()
            if checkName:
                return {"status":0,"msg":"Lead status already exists."}
            else:
                Newtype = LeadStatus(
                    name=name,
                    created_by = user.id,
                    created_at = datetime.now(settings.tz_IN),
                    updated_at = datetime.now(settings.tz_IN),
                    status = 1
                )
                db.add(Newtype)
                db.commit()
                return {"status":1,'msg':"Lead status successfully created."}
        else:
            return {'status':0,"msg":"You are not authenticated to create lead status."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/update_lead_status")
async def updateLeadStatus(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         dataId :int=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            return {"status":0,"msg":"Editing this status is restricted"}

            getLeadStatus = db.query(LeadStatus).filter(LeadStatus.status==1)
            checkId = getLeadStatus.filter(LeadStatus.id == dataId).first()
            if checkId:
                checkName = getLeadStatus.filter(LeadStatus.name==name,
                                               LeadStatus.id != dataId).first()
                if checkName:
                    return {"status":0,"msg":"Lead status already exists."}
                else:
                    checkId.name = name
                    checkId.created_by = user.id
                    checkId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()
                    return {"status":1,"msg":"Lead status successfully updated."}
            else:
                return {"status":1,"msg":"Invalid lead status."}
        else:
            return {'status':0,"msg":"You are not authenticated to update lead status."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/list_lead_status")
async def listLeadStatus(db:Session =Depends(deps.get_db),
                       token:str = Form(...),
                       page:int=1,size:int = 10,
                       name:str = Form(None)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllLeadStatus = db.query(LeadStatus).filter(LeadStatus.status==1)
            if name:
                getAllLeadStatus = getAllLeadStatus.filter(LeadStatus.name.like("%"+name+"%"))
            getAllLeadStatus = getAllLeadStatus.order_by(LeadStatus.name.asc())

            totalCount = getAllLeadStatus.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllLeadStatus = getAllLeadStatus.limit(limit).offset(offset).all()

            dataList=[]
            if getAllLeadStatus:
                for row in getAllLeadStatus:
                    dataList.append(
                        {
                            "LeadStatusId":row.id,
                            "LeadStatusName":row.name,
                            "createdBy":row.user.user_name if row.user else None,
                            "createdAt":row.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "dataStatus":row.status
                        }
                    )
            
            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
        
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to view lead status."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


@router.post("/delete_lead_status")
async def deleteLeadStatus(db:Session =Depends(deps.get_db),
                                 token:str = Form(...),dataId:int=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        return {"status":0,"msg":"Deleting this status is restricted"}
        if user.user_type == 1:
            deleteData = db.query(LeadStatus)\
                .filter(LeadStatus.id == dataId,LeadStatus.status ==1 ).update({"status":-1})
            db.commit()
            return {'status':1,"msg":"Lead status successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete lead status."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})
    
#Competitor
@router.post("/create_competitor")
async def createCompetitor(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            checkName = db.query(Competitors).\
                filter(Competitors.name ==name ,
                       Competitors.status ==1).first()
            if checkName:
                return {"status":0,"msg":"Competitor already exists."}
            else:
                Newtype = Competitors(
                    name=name,
                    created_by = user.id,
                    created_at = datetime.now(settings.tz_IN),
                    updated_at = datetime.now(settings.tz_IN),
                    status = 1
                )
                db.add(Newtype)
                db.commit()
                return {"status":1,'msg':"Competitor successfully created."}
        else:
            return {'status':0,"msg":"You are not authenticated to create competitor."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/update_competitor")
async def updateCompetitors(db:Session=Depends(deps.get_db),
                         token:str=Form(...),
                         dataId :int=Form(...),
                         name:str=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getCompetitors = db.query(Competitors).filter(Competitors.status==1)
            checkId = getCompetitors.filter(Competitors.id == dataId).first()
            if checkId:
                checkName = getCompetitors.filter(Competitors.name==name,
                                               Competitors.id != dataId).first()
                if checkName:
                    return {"status":0,"msg":"Competitor already exists."}
                else:
                    checkId.name = name
                    checkId.created_by = user.id
                    checkId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()
                    return {"status":1,"msg":"Competitor successfully updated."}
            else:
                return {"status":1,"msg":"Invalid lead status."}
        else:
            return {'status':0,"msg":"You are not authenticated to update competitors."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

@router.post("/list_competitors")
async def listCompetitors(db:Session =Depends(deps.get_db),
                       token:str = Form(...),
                       page:int=1,size:int = 10,
                       name:str = Form(None)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type in [1,2]:
            getAllCompetitors = db.query(Competitors).filter(Competitors.status ==1)
            if name:
                getAllCompetitors = getAllCompetitors.filter(Competitors.name.like("%"+name+"%"))
            getAllCompetitors = getAllCompetitors.order_by(Competitors.name.asc())

            totalCount = getAllCompetitors.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllCompetitors = getAllCompetitors.limit(limit).offset(offset).all()

            dataList=[]
            if getAllCompetitors:
                for row in getAllCompetitors:
                    dataList.append(
                        {
                            "CompetitorsId":row.id,
                            "CompetitorsName":row.name,
                            "createdBy":row.user.user_name,
                            "createdAt":row.updated_at.strftime("%Y-%m-%d %H:%M:%S")
                        }
                    )
            
            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
        
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to view competitors."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})


@router.post("/delete_Competitors")
async def deleteCompetitors(db:Session =Depends(deps.get_db),
                                 token:str = Form(...),dataId:int=Form(...)):
    user=deps.get_user_token(db=db,token=token)
    if user:
        if user.user_type == 1:
            deleteData = db.query(Competitors)\
                .filter(Competitors.id == dataId,Competitors.status ==1 ).update({"status":-1})
            db.commit()
            return {'status':1,"msg":"Competitors successfully deleted."}
        else:
            return {'status':0,"msg":"You are not authenticated to delete competitors."}
    else:
        return ({"status": -1,"msg": "Sorry your login session expires.Please login again."})

