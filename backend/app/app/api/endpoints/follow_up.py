from fastapi import APIRouter, Depends, Form,requests
from sqlalchemy.orm import Session,joinedload,subqueryload
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_
from app.core import security
from fastapi import APIRouter, Depends, Form,requests,UploadFile,File
from typing import Optional,List
# from app.api.endpoints.lead import scheduler,scheduled_task
# from apscheduler.jobstores.base import JobLookupError


router = APIRouter()

@router.post("/add_followup")
async def addFollowUp(db:Session = Depends(deps.get_db),
                         token:str = Form(...),
                        enquiry_type:int=Form(None),
                         lead_id:int=Form(...),
                         followup_dt:datetime=Form(...),
                         comment:str=Form(None),
                        upload_file:Optional[List[UploadFile]] = File(default=None)
                         ):
    user = deps.get_user_token(db=db , token=token)
    if user:

        getLead = db.query(Lead).filter(Lead.id==lead_id).first()
        today = datetime.now()

        if followup_dt<today:
            return{"status":0,"msg":"Only future datetime are allowed."}


        followup_dt =followup_dt.strftime('%Y-%m-%d %H:%M')
        # followup_dt =followup_dt.date()

        historyId = None

        inCompletefollowUp = db.query(FollowUp).filter(FollowUp.status==1,
                            FollowUp.lead_id==lead_id,FollowUp.followup_status==1).first()
        
        if inCompletefollowUp:
            inCompletefollowUp.followup_status=-1
            # return {"status":0,"msg":"This lead already has an incomplete follow-up scheduled."}
        
        commentTemplate =f"{comment} (The follow-up date is scheduled for {followup_dt})"

        if not comment:
            commentTemplate=f"The follow-up date is scheduled for {followup_dt}"

        getLead.schedule_date = followup_dt
        getLead.is_followup = 1

       
        newFollowUp = FollowUp(
            lead_id= lead_id,
            followup_dt = followup_dt,
            createdBy = user.id,
            comment = commentTemplate,
            enquiry_type_id =enquiry_type,
            followup_status = 1,
            created_at = datetime.now(settings.tz_IN),
            status = 1 )
        db.add(newFollowUp)
        db.commit()


        addHistory = LeadHistory(
            lead_id= lead_id,
            followup_id = newFollowUp.id,
            leadStatus = "Follow up",
            lead_status_id =5,
            enquiry_type_id =enquiry_type,

            changedBy= user.id,
            comment = commentTemplate,
            created_at = datetime.now(settings.tz_IN),
            status = 1
        )
        db.add(addHistory)
        db.commit()
        historyId = addHistory.id

        # try:
        #     scheduler.remove_job(f"{getLead.id}")
        #     print("hai")

        #         # print(f"Job {user_id} removed successfully")
        # except JobLookupError:
        #         pass
        # scheduler.add_job(scheduled_task, 'date', id=f"{getLead.id}",run_date=getLead.schedule_date,args=[db,getLead.id])


        if upload_file and upload_file != None:
                    
            for i in range(len(upload_file)):  
                
                store_fname = upload_file[i].filename
                
                f_name,*etn = store_fname.split(".")
            
                file_path,file_exe = file_storage(upload_file[i],f_name)
                add_file = LeadMedia(
                    lead_id = lead_id,
                    followup_id = newFollowUp.id,
                    url = file_exe,
                    lead_history_id = addHistory.id,
                    created_at = datetime.now(tz=settings.tz_IN),
                    upload_by = user.id,
                    status = 1,
                )  
                db.add(add_file)  
                db.commit()  

        return {"status":1,"msg":'FollowUp successfully created.'}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    

# @router.post('/edit_followup')
# async def editFollowup(db:Session=Depends(deps.get_db),
#                        token:str=Form(...),followup_id:int=Form(...),
#                        comment:str=Form(None),
#                        followup_dt:datetime=Form(...),
#                         upload_file:Optional[List[UploadFile]] = File(default=None)
#                        ):
#     user = deps.get_user_token(db=db , token=token)
#     if user:
#         getFollowup = db.query(FollowUp).filter(FollowUp.status==1,
#                                                 FollowUp.id == followup_id ).first()
        
#         # followup_dt =followup_dt.strftime('%Y-%m-%d %H:%M')
#         # oldFollowUp = getFollowup.lead.schedule_date.strftime('%Y-%m-%d %H:%M')
#         followup_dt =followup_dt.date()
#         oldFollowUp = getFollowup.lead.schedule_date.date()

#         historyId=None
#         followUpSts=["-","FollowUp","Completed","Canceled"]


#         commentTemplate = comment
#         if followup_dt!=oldFollowUp:

#             if comment and (comment!=getFollowup.comment)  :
#                 commentTemplate =f"{comment} (The user updated the follow-up date is {followup_dt})"

#             if not comment:
#                 commentTemplate=f"The user updated the follow-up date is {followup_dt}"

#         if followup_dt!=oldFollowUp or ((comment!=getFollowup.comment) and comment ):

#             getFollowup.comment = commentTemplate
#             getFollowup.followup_dt = followup_dt
#             getFollowup.updated_at = datetime.now(settings.tz_IN)

#             getFollowup.lead.schedule_date = followup_dt
#             db.commit()

#             addHistory = LeadHistory(
#                 lead_id= getFollowup.lead_id,
#                 followup_id = getFollowup.id,
#                 changedBy= user.id,
#                 leadStatus =followUpSts[getFollowup.followup_status],
#                 comment = commentTemplate,
#                 created_at = datetime.now(settings.tz_IN),
#                 status = 1
#             )
#             db.add(addHistory)
#             db.commit()
#             historyId=addHistory.id

#         if upload_file and upload_file != None:
                    
#             for i in range(len(upload_file)):  
                
#                 store_fname = upload_file[i].filename
                
#                 f_name,*etn = store_fname.split(".")
            
#                 file_path,file_exe = file_storage(upload_file[i],f_name)
#                 add_file = LeadMedia(
#                     lead_id =  getFollowup.lead_id,
#                     url = file_exe,
#                     followup_id = getFollowup.id,
#                     lead_history_id = historyId,
#                     created_at = datetime.now(tz=settings.tz_IN),
#                     upload_by = user.id,
#                     status = 1,
#                 )  
#                 db.add(add_file)  
#                 db.commit()  

#         return {'status':1,"msg":"FollowUp successfully updated."}
#     else:
#         return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    

# @router.post('/update_followup')
# async def updateFollowup(db:Session=Depends(deps.get_db),
#                        token:str=Form(...),followup_id:int=Form(...),
#                        comment:str=Form(None),
#                        followup_status:int=Form(...,description=" 1->follow_up,2-completed,-1->cancelled"),
#                         upload_file:Optional[List[UploadFile]] = File(default=None)
#                        ):
    
#     user = deps.get_user_token(db=db , token=token)
#     if user:
#         getFollowup = db.query(FollowUp).filter(FollowUp.status==1,
#                                                 FollowUp.id == followup_id ).first()
        
#         historyId =None
        
#         commentTemplate = comment
#         followUpSts=["-","FollowUp","Completed","Canceled"]

#         if followup_status!=getFollowup.followup_status:
#             if comment and (comment!=getFollowup.comment)  :
#                 commentTemplate =f"{comment} (The user updated the status is {followUpSts[followup_status]})"

#             if not comment:
#                 commentTemplate=f"The user updated the status is {followUpSts[followup_status]}"

#         if followup_status!=getFollowup.followup_status or ((comment!=getFollowup.comment) and comment ):
        
#             getFollowup.comment = commentTemplate
#             getFollowup.followup_status = followup_status
#             getFollowup.updated_at = datetime.now(settings.tz_IN)

#             #update in lead
#             getFollowup.lead.updated_at = datetime.now(settings.tz_IN)
#             getFollowup.lead.is_followup = followup_status
#             db.commit()

#             addHistory = LeadHistory(
#                 lead_id= getFollowup.lead_id,
#                 followup_id = followup_id,
#                 leadStatus = followUpSts[followup_status],
#                 changedBy= user.id,
#                 comment = commentTemplate,
#                 created_at = datetime.now(settings.tz_IN),
#                 status = 1
#             )
#             db.add(addHistory)
#             db.commit()
#             historyId = addHistory.id

#         if upload_file and upload_file != None:
                    
#             for i in range(len(upload_file)):  
                
#                 store_fname = upload_file[i].filename
                
#                 f_name,*etn = store_fname.split(".")
            
#                 file_path,file_exe = file_storage(upload_file[i],f_name)
#                 add_file = LeadMedia(
#                     lead_id =  getFollowup.lead_id,
#                     followup_id=getFollowup.id,
#                     url = file_exe,
#                     lead_history_id = historyId,
#                     created_at = datetime.now(tz=settings.tz_IN),
#                     upload_by = user.id,
#                     status = 1,
#                 )  
#                 db.add(add_file)  
#                 db.commit()  
            
#             return {'status':1,"msg":"FollowUp Status successfully Changed."}
#         else:
#             return{"status":0,"msg":"no comments"}
#     else:
#         return {"status":-1,"msg":"Sorry your login session expires.Please login again. "}
    

@router.post("/list_followup")
async def list_followup(db: Session = Depends(deps.get_db),
                   token:str = Form(...),page:int=1,size:int=10,
                   followup_status:int=Form(None),
                   leadId:int =Form(...),
                   followup_id:int=Form(None)):
    
    user = deps.get_user_token(db=db,token=token)
    if user:

        getLead = db.query(Lead).filter(Lead.status,Lead.id==leadId).first()

        if not getLead:
            return {"status":0,"msg":"No Lead Found"}

        getFollowUp = db.query(FollowUp).filter(FollowUp.lead_id == leadId, FollowUp.status == 1)

        if followup_id:
            getFollowUp = getFollowUp.filter(FollowUp.id==followup_id)

        if followup_status:
            getFollowUp = getFollowUp.filter(FollowUp.followup_status==followup_status)
        
        getFollowUp = getFollowUp.order_by(FollowUp.id.desc())

        totalCount = getFollowUp.count()
        
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getFollowUp = getFollowUp.offset(offset).limit(limit)
            
        getFollowUp = getFollowUp.all()

        dataList = []

        data=({"page":page,"size":size,
                "total_page":totalPage,
                "total_count":totalCount,
                "items":dataList})
   
        if not getFollowUp:
            return {"status":1,"msg":"No data found","data":data}
        

        for row in getFollowUp:
            # followUpSts=["-","FollowUp","Completed","Canceled"]
            followUpSts=["-","Active","Inactive"]
# 

            historyList = []

            getHistory = db.query(LeadHistory).\
                filter(LeadHistory.followup_id==row.id).order_by(LeadHistory.id.desc()).all()
            
            #use->without query in loop and order desc
            # for file in sorted(row.lead_media, key=lambda x: x.id, reverse=True):
            #     mediaList.append({
            #         "file_id":file.id,
            #         "url":f"{settings.BASE_DOMAIN}{file.url}",
            #     })

            for history in getHistory:
                historyList.append({
                    "history_id":history.id,
                    "comment":history.comment,
                    "followup_status":history.leadStatus,
                    "changed_by":row.user.name,
                    "created_at":history.created_at
                })

            mediaList=[]

            getMedia = db.query(LeadMedia).\
                filter(LeadMedia.followup_id==row.id,LeadMedia.status==1).order_by(LeadMedia.id.desc()).all()
            
            for file in getMedia:
                mediaList.append({
                    "file_id":file.id,
                    "url":f"{settings.BASE_DOMAIN}{file.url}",
                })

            dataList.append(
                {
                    "followup_id":row.id,
                    "followup_status":followUpSts[row.followup_status],
                    "followup_dt":row.followup_dt,
                    "enquiry_type":row.enquiry_type.name if row.enquiry_type_id else None,
                    "created_by":row.user.name,
                    "updated_at":row.updated_at,
                    "enquiry_type_id":row.enquiry_type_id,

                    "created_at":row.created_at,
                    "comment":row.comment,
                    "history":historyList,
                    "files":mediaList
                })
            
        data=({"page":page,"size":size,
                "total_page":totalPage,
                "total_count":totalCount,
                "is_followup":getLead.is_followup,
                "items":dataList})
        return ({"status":1,"msg":"Success","data":data})
    
    else:
        return {"status":-1,"msg":"Your login session expires.Please login again."}


# @router.post("/delete_followup")
# async def deleteFollowUp(db:Session=Depends(deps.get_db),
#                          token:str=Form(...),
#                          followup_id:int=Form(...)):
#     user = deps.get_user_token(db=db,token=token)
#     if user:

#         deleteFollowUp = db.query(FollowUp).\
#             filter(FollowUp.id == followup_id).first()
#         deleteFollowUp.status=-1
#         deleteFollowUp.lead.is_followup=-1

#         filesToDel = db.query(LeadMedia)\
#                     .filter(LeadMedia.status == -1, LeadMedia.followup_id==followup_id)
        
#         delFiles = filesToDel.update({"status":-1})
        
#         for file in filesToDel.all():
#             file_loc = settings.BASE_UPLOAD_FOLDER +"/"+ file.url
#             if os.path.exists(file_loc):
#                 os.remove(file_loc)

#         db.commit()

#         return {"status":1,"msg":"FollowUp details successfully removed."}
#     else:
#         return {"status":-1,"msg":"Your login session expires.Please login again."}


@router.post("/active_inactive_followup")
async def activeInactiveFollowUp(db:Session=Depends(deps.get_db),
                             token:str=Form(...),lead_id:int=Form(...),
                             activeStatus:int=Form(...,description="1->active,-1->inactive")):
    user = deps.get_user_token(db=db,token=token)
    if user:
        # getFollowUp = db.query(FollowUp).filter(FollowUp.id == followup_id,
        #                                 FollowUp.status == 1).first()
        getFollowUp = db.query(FollowUp).filter(FollowUp.lead_id == lead_id,FollowUp.status == 1)

        # try:
        #     scheduler.remove_job(f"{lead_id}")
        #         # print(f"Job {user_id} removed successfully")
        # except JobLookupError:
        #         pass
        
        
        if activeStatus==1:
            getFollowUp=getFollowUp.filter(FollowUp.followup_status==-1)

        if activeStatus==-1:
            getFollowUp=getFollowUp.filter(FollowUp.followup_status==1)

        getFollowUp=getFollowUp.order_by(FollowUp.id.desc()).first()
        
        if not getFollowUp : 
            return {"status":0,"msg":"No followup found"}            
       
        
        anyActiveFolUp = db.query(FollowUp).filter(FollowUp.id != getFollowUp.id,
                                                   FollowUp.lead_id==getFollowUp.lead_id,
                                            FollowUp.followup_status==1,       
                                        FollowUp.status == 1).first()


        
        if anyActiveFolUp and activeStatus==1:
            return {"status":0,"msg":"This lead already has an incomplete follow-up scheduled."}            
        
        followUpSts = 1 if activeStatus==1 else -1
        getFollowUp.followup_status=followUpSts
        getFollowUp.lead.is_followup=followUpSts
        db.commit()

        comment="activated" if activeStatus==1 else "deactivated"
        commentTemplate = f'FollowUp {comment}'

        addHistory = LeadHistory(
            lead_id= getFollowUp.lead_id,
            followup_id = getFollowUp.id,
            changedBy= user.id,
            leadStatus = comment,
            comment = commentTemplate,
            created_at = datetime.now(settings.tz_IN),
            status = 1
            )
        db.add(addHistory)
        getFollowUp.comment = commentTemplate
        db.commit()
        message ="Success."
        if activeStatus ==1:
            message ="FollowUp successfully activated."
        else:
            message ="FollowUp successfully deactivated."

        return {"status":1,"msg":message}
    else:
        return {'status':0,"msg":"You are not authenticated to change status of any user"}