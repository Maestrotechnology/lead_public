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

@router.post("/create_industry")
async def CreateIndustry(db:Session = Depends(deps.get_db),
                         token:str = Form(...),name:str=Form(...),
                         industryType:str=Form(None),description:str=Form(None)
                         ):
    user = deps.get_user_token(db=db , token=token)
    if user:
        if user.user_type ==1:
            checkName = db.query(Industry).\
                filter(Industry.name==name,Industry.status==1).first()
            if checkName:
                return {'status':0,"msg":"Industry name already in the record."}
            else:
                newIndustry = Industry(
                    name= name,
                    industry_type = industryType,
                    description = description,
                    created_at = datetime.now(settings.tz_IN),
                    status = 1 )
                db.add(newIndustry)
                db.commit()
                return {"status":1,"msg":'Industry successfully created.'}
        else:
            return {'status':0,"msg":"You are not authenticated to create industry."}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    
@router.post('edit_industry')
async def editIndustry(db:Session=Depends(deps.get_db),
                       token:str=Form(...),industryId:int=Form(...),
                       name:str=Form(...),
                        industryType:str=Form(None),description:str=Form(None)
                       ):
    user = deps.get_user_token(db=db , token=token)
    if user:
        if user.user_type ==1:
            getIndustry = db.query(Industry).filter(Industry.status==1)
            checkIndustryId= getIndustry.filter(Industry.id == industryId ).first()
            if not checkIndustryId:
                return {'status':0,"msg":"No record found."}
            else:
                checkName = getIndustry.filter(Industry.name == name ,
                                               Industry.id != industryId ).first()
                if checkName:
                    return {'status':0,"msg":"Industry name already in the record."}
                else:
                    checkIndustryId.name = name
                    checkIndustryId.industry_type = industryType
                    checkIndustryId.description = description
                    checkIndustryId.updated_at = datetime.now(settings.tz_IN)
                    db.commit()

                    return {'status':1,"msg":"Industry successfully updated."}
        else:
            return {'status':0,"msg":"You are not authenticated to edit industry."}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    
@router.post("/listIndustry")
async def listIndustry(db:Session=Depends(deps.get_db),
                       token:str=Form(...),page:int = 1,size:int=10,
                       name:str = Form(None)):
    
    user = deps.get_user_token(db=db , token=token)
    if user:
        if user.user_type ==1:
            getAllIndustry = db.query(Industry).filter(Industry.status==1)
            if name:
                getAllIndustry = getAllIndustry.filter(Industry.like("%"+name+"%"))
            getAllIndustry = getAllIndustry.order_by(Industry.name.asc())
            totalCount = getAllIndustry.count()
            totalPages,offset,limit = get_pagination(totalCount,page,size)
            getAllIndustry = getAllIndustry.limit(limit).offset(offset).all()

            dataList=[]
            if getAllIndustry:
                for row in getAllIndustry:
                    dataList.append({
                        "industryId":row.id,
                        "industryType":row.industry_type,
                        "description":row.description,
                        "created_at":row.created_at
                    })

            data=({"page":page,"size":size,
                   "total_page":totalPages,
                   "total_count":totalCount,
                   "items":dataList})
            return ({"status":1,"msg":"Success","data":data})
        else:
            return {'status':0,"msg":"You are not authenticated to see industry."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}

@router.post("/delete_industry")
async def deleteIndustry(db:Session=Depends(deps.get_db),
                       token:str=Form(...),industryId:int=Form(...)):
    user = deps.get_user_token(db=db , token=token)
    if user:
        if user.user_type ==1:
    
            checkIndustryId= db.query(Industry).\
                filter(Industry.id == industryId , Industry.status==1).update({"status":-1})
            db.commit()
            return {"status":1,"msg":"Industry successfully deleted"}
        else:
            return {'status':0,"msg":"You are not authenticated to delete industry."}
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}