from fastapi import APIRouter, Depends, Form,requests
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_,func,case
from app.core import security

import random


router = APIRouter()
@router.post("/all_data_count")
async def allDataCount (db:Session = Depends(deps.get_db),
                        token:str=Form(...)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        today = datetime.now(settings.tz_IN)

       
        fromdatetime = today.replace(day=1,month=1).strftime("%Y-%m-%d 00:00:00")
        
        todatetime = today.replace(day=31,month=12).strftime("%Y-%m-%d 23:59:59")        
        getTotalData = (
            db.query(
                func.count(case((Lead.status == 1, 1))).label("total"),
                func.count(case((Lead.lead_status_id == 2, 1))).label("assigned"),
                func.count(case((Lead.lead_status_id == 8, 1))).label("demo_poc"),
                func.count(case((Lead.lead_status_id == 4, 1))).label("quotation"),
                func.count(case((Lead.is_followup == 1, 1))).label("followup"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("orders"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("missed"),
            )
        ).filter(Lead.lead_status_id!=7,Lead.status == 1,Lead.update_at.between(fromdatetime,todatetime))

        getMissedLead = db.query(
                func.count(Lead.id)).filter(Lead.status == 1,
                                            # Lead.lead_status_id==5,
                                            Lead.is_followup==1,
                                            Lead.lead_status_id!=7,
                                            Lead.update_at.between(fromdatetime,todatetime),
                                            func.DATE_FORMAT(Lead.schedule_date, '%Y-%m-%d %H:%M') < (today.strftime('%Y-%m-%d %H:%M')))

        if user.user_type == 3:
            getTotalData = getTotalData.filter(Lead.dealer_id == user.id,Lead.lead_status_id != 17)
            getMissedLead = getMissedLead.filter(Lead.dealer_id == user.id,Lead.lead_status_id != 17)

        elif user.user_type == 4:
            getTotalData = getTotalData.filter(Lead.assigned_to == user.id,Lead.lead_status_id != 17)
            getMissedLead = getMissedLead.filter(Lead.dealer_id == user.id,Lead.lead_status_id != 17)


        getMissedLead = getMissedLead.all()

        # getMissed = db.query(
        #         (Lead.id)).filter(Lead.status == 1,
        #                                     # Lead.lead_status_id==5,
        #                                     Lead.is_followup==1,
        #                                     Lead.update_at.between(fromdatetime,todatetime),
        #                                     func.DATE_FORMAT(Lead.schedule_date, '%Y-%m-%d %H:%M') < (today.strftime('%Y-%m-%d %H:%M')))

        # for i in getMissed.all():
        #     print(i.id)

        threshold_datetime = datetime.now(settings.tz_IN) - timedelta(hours=24)
        count = 0
        leadStatusData =[6,7,17]
        
        getOverDude = getTotalData.filter(Lead.lead_status_id.notin_(leadStatusData),Lead.update_at <= threshold_datetime ).first()
        
        getTotalData = getTotalData.first()

        data = [
            {
            "displayName":"Total Leads",
            "key":"total_counts",
            "value":getTotalData.total,
            "colorCode":"#328CD1",
            "type":1,
            "leads":{"displayName":"Leads","value":getTotalData.total },
            "over_due":{"displayName":"Over Due","value":getOverDude.total}},
            # {
            # "displayName":"Assigned Leads",
            # "key":"assigned_count",
            # "value":getTotalData.assigned,
            # "colorCode":"#2AB95A",
            # "type":2,
            # "leads":{"displayName":"Leads","value":getTotalData.assigned - getOverDude.assigned},
            # "over_due":{"displayName":"Over Due","value":getOverDude.assigned}},
              {
            "displayName":"Missed",
            "key":"missed_count",
            "value":getMissedLead[0][0],
            "colorCode":"#8154FF",
            "type":9,
            "leads":{"displayName":"Leads","value":getMissedLead[0][0]},
            "over_due":{"displayName":"Over Due","value":0}
        },
            {
            "displayName":"Followup",
            "key":"followup_count",
            "value":getTotalData.followup,
            "colorCode":"#FA5B62",
            "type":5,
            "leads":{"displayName":"Leads","value":getTotalData.followup },
            "over_due":{"displayName":"Over Due","value":getMissedLead[0][0]}
        },
             {
            "displayName":"Demo/Poc",
            "key":"poc_count",
            "value":getTotalData.demo_poc,
            "colorCode":"#2AB95A",
            "type":8,
            "leads":{"displayName":"Leads","value":getTotalData.demo_poc},
            "over_due":{"displayName":"Over Due","value":0}},
         
        {
            "displayName":"Quotation",
            "key":"quotation_count",
            "value":getTotalData.quotation,
            "colorCode":"#EB9C04",
            "leads":{"displayName":"Leads","value":getTotalData.quotation },
            "over_due":{"displayName":"Over Due","value":getOverDude.quotation},
            "type":4
        },
        

        {
            "displayName":"Orders",
            "key":"orders_count",
            "value":getTotalData.orders,
            "colorCode":"#F87A05",
            "type":6,
            "leads":{"displayName":"Leads","value":getTotalData.orders },
            "over_due":{"displayName":"Over Due","value":getOverDude.orders}
        },
      
                {
            "displayName":"Canceled",
            "key":"canceled_count",
            "value":getTotalData.missed,
            "colorCode":"#8154FF",
            "type":7,
            "leads":{"displayName":"Leads","value":getTotalData.missed},
            "over_due":{"displayName":"Over Due","value":0}
        },
   ]
        
        return {"status":1,'msg':"Success.","data":data}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}

@router.post("/dealer_wise_report")
async def dealerWiseReport(db:Session=Depends(deps.get_db),token:str=Form(None),dealerId:int=Form(None),page:int=1,size:int=10):
    user = deps.get_user_token(db=db,token=token)
    if user:
        today = datetime.now()
        twenty_four_hours_ago = today - timedelta(hours=24)
        
        fromdatetime = today.replace(day=1,month=1,hour=0,minute=0,second=0)
        todatetime = today.replace(hour=23,minute=59,second=59)

        getAllDealer =  db.query(User.id,User.name).filter(User.status==1,User.user_type == 3)
        if dealerId:
            getAllDealer = getAllDealer.filter(User.id == dealerId)

        totalCount = getAllDealer.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllDealer = getAllDealer.order_by(User.name.asc()).limit(limit).offset(offset).all()

        dataList =[]
        for dealer in getAllDealer:
            total,follow_up,close=getStatusData(db,fromdatetime,todatetime,dealer.id)
            dataList.append({
                "Dealer":dealer.name,
                "dealer_id": dealer.id,
                "totalLead":total ,
                "active_followUp":follow_up,
                'active_close':close,
            })
    
        data=({"page":page,"size":size,
                    "total_page":totalPage,
                    "total_count":totalCount,
                    "items":dataList})
        return ({"status":1,"msg":"Success","data":data})
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}



def getStatusData(db:Session,fromdatetime,todatetime,dealerId:int):
    
    # newDate = datetime.now() - timedelta(hours=24)
    getTotalData = db.query(
                func.count(case((Lead.status == 1, 1))).label("all"),
                # func.count(case((Lead.lead_status_id.in_([4,5]), 1))).label("follow_up"),
                func.count(case((Lead.is_followup==1, 1))).label("follow_up"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("close"),
            ) .filter(Lead.update_at.between(fromdatetime,todatetime),Lead.status == 1)
        
    
    getTotalData = getTotalData.filter(Lead.dealer_id == dealerId )
    # leadStatusData =[6,7,17]
    # if dateData:    
        
    #     getTotalData = getTotalData.filter(Lead.lead_status_id.not_in(leadStatusData),Lead.update_at <= dateData)
    # else:
    #     getTotalData = getTotalData.filter(or_(Lead.update_at >= newDate,and_(Lead.lead_status_id.in_(leadStatusData),Lead.update_at <= newDate)))
    getTotalData = getTotalData.all()


    if getTotalData:
        for data in getTotalData:
            return data
    return 0,0,0
            



