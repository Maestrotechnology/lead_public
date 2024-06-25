from fastapi import APIRouter, Depends, Form,UploadFile,File
from app.api import deps
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models import *
from app.utils import *
from datetime import datetime,date
from typing import List, Optional,Union
from sqlalchemy import *

router=APIRouter()

#Upload File


    
@router.post("/list_leadmedia")
async def listFileUpload(*,db: Session = Depends(deps.get_db),
                           token:str = Form(...),lead_id:int=Form(None),
                          page: int=1,size: int=10,
                ):
    
    user = deps.get_user_token(db=db,token=token)


    if user:
        dataLt = []
        
        getFile =  db.query(LeadMedia).filter(LeadMedia.status == 1)

        if lead_id:
            getFile = getFile.filter(LeadMedia.lead_id==lead_id)

        totalCount = getFile.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getFile = getFile.order_by(LeadMedia.id.desc())

        getFile = getFile.offset(offset).limit(limit).all()
                                    
        for row in getFile:
            dataLt.append({
                "file_id":row.id,
                "url":f"{settings.BASE_DOMAIN}{row.url}",
            })
            
        return({"status":1,"msg":"Success","page":page,"size":size,
            "total_page":totalPage,
            "total_count":totalCount,"data":dataLt})
    
    else:
        return({"status":0,"msg":"Invalid Request"})
    
#View File 

@router.post("/view_lead_media")
async def view_file(*,db:Session=Depends(deps.get_db),
                token:str = Form(...),
                file_id:int=Form(...)):
    
    user = deps.get_user_token(db=db,token=token)


    if user:

        getFile=db.query(LeadMedia).filter(
            LeadMedia.id == file_id,
            LeadMedia.status == 1).first()
        
        if not getFile:
            return {"status":0,"msg":"Invalid File Id"}
            
        
        fileProfile={}
        if getFile:
            fileProfile.update({"file_id":getFile.id,
                "lead_id":getFile.lead_id,
                "upload_by":getFile.upload_by,
                "url":getFile.file,
                "created_at":getFile.created_at,
                "status":getFile.status,
                            })
        
            return {"status": 1, "msg": "Success", "data": fileProfile}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }
    

#Delete File

@router.post("/delete_lead_media")
async def delete_file(*,db:Session=Depends(deps.get_db),
                      token:str=Form(...),
                      lead_id:int =Form(None),
                      delete_all:int=Form(None,description="1-delete_all"),
                      lead_history_id:int=Form(None),
                file_id:int=Form(...)):
    
    user = deps.get_user_token(db=db,token=token)

    if user:

        allFiles = db.query(LeadMedia).filter(LeadMedia.status==1)

        if delete_all==1:
            allFiles = allFiles.filter(LeadMedia.lead_id==lead_id).update({"status":-1})
        
        if file_id:
            allFiles = allFiles.filter(LeadMedia.id==file_id).update({"status":-1})

        db.commit()
        return{"status":1,"msg":"Successfully Deleted"}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }