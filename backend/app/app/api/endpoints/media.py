from fastapi import APIRouter, Depends, Form,requests,UploadFile,File
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_,func,case,extract
from typing import List, Optional

router = APIRouter()

@router.post("/uploadFile")
async def uploadFile(db:Session=Depends(deps.get_db),
                     token:str = Form(...),
                     requirement_id: int = Form(...),
                     file_title: str = Form(None),
                     upload_file: Optional[List[UploadFile]] = File(None),
                     file_type:int=Form(...,description="1-video,2-photo"),
                     ):
    user = deps.get_user_token(db=db,token=token)
    if user:
        checkRequirement = db.query(Requirements).filter(
            Requirements.id == requirement_id,Requirements.status == 1 ).first()
        if not checkRequirement:
            return {"status":0,"msg":"No requirements record found."}
        else:
            if upload_file:
                row = 0
                imageData =[]
                for file in upload_file:
                    uploadedFile = file.filename
                    fName,*etn = uploadedFile.split(".")
                    filePath,returnFilePath = file_storage(file,fName)
                    splited_filename = file_title.split(',') if file_title else None
                    imageData.append({
                        "name" : (splited_filename[row]
                                        if splited_filename and 
                                        splited_filename[row] 
                                        else fName),
                        "requirement_id" :requirement_id,
                        "file_type":file_type,
                        "url" : returnFilePath,
                        "created_at" : datetime.now(settings.tz_IN),
                        "status" : 1
                    })
                    row += 1
                try:
                    with db as conn:
                        conn.execute(Media.__table__.insert().values(imageData))
                        conn.commit()
                    return({"status": 1,"msg": "Uploaded Successfully."})
                
                except Exception as e:
                    
                    print(f"Error during bulk insert: {str(e)}")
                    return {"status": 0,"msg": "Failed to insert image"}

            else:
                return {"status": 0,"msg": "No file is selected."}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}


@router.post("/listMedia")
async def listMedia(db:Session = Depends(deps.get_db),
                        token:str = Form(...),requirementId:int=Form(None),
                          page: int=1,size: int=10,file_type:int=Form(...,description="1-video,2-image")):
    user = deps.get_user_token(db=db,token=token)
    if  user:
        getAllMedia = db.query(Media).filter(Media.status == 1,Media.file_type == file_type)
        if requirementId:
            getAllMedia = getAllMedia.filter(Media.requirement_id == requirementId)
        
        getAllMedia = getAllMedia.order_by(Media.id.desc())

        attachmentCount = getAllMedia.count()
        totalPages, offset , limit = get_pagination(attachmentCount,page,size)
        getAllMedia = getAllMedia.limit(limit).offset(offset).all()

        dataList = []
        if getAllMedia:
            for row in getAllMedia:
                dataList.append({
                    "MediaID":row.id,
                    "MediaPath": f"{settings.BASE_DOMAIN}{row.url}",
                    "MediaName": row.name
                })
        data=({"page": page,"size": size,"total_page": totalPages,
               "total_count": attachmentCount,"items": dataList})
        return {"status": 1,"msg": "success","data": data}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}

@router.post("/deleteAttachments")
async def deleteAttachments(db: Session = Depends(deps.get_db),
                            token:str = Form(...),
                            mediaId: int = Form(...)):
    user = deps.get_user_token(db=db,token=token)
    
    if  user:
        deleteAttachment = db.query(Media).filter(
            Media.id == mediaId,
            Media.status == 1
        ).update({"status": -1})
        db.commit()
        return {"status": 1,"msg": "Media deleted successfully"}
    return {"status":-1,"msg":"Sorry your login session expires.Please login again."}


