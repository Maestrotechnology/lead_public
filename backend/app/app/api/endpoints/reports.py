
from fastapi import APIRouter, Depends, Form,requests
from sqlalchemy.orm import Session
from app.models import ApiTokens,User
from app.api import deps
from app.core.config import settings
from app.core.security import get_password_hash,verify_password
from datetime import datetime
from app.utils import *
from sqlalchemy import or_,func,case,extract
from app.core import security

import random


router = APIRouter()

@router.post("/leadReport")
async def leadReport(db:Session=Depends(deps.get_db),
                     token:str = Form(...),fromDateTime :datetime=Form(None),
                     toDatetime : datetime = Form(None)
                     ,isLineChart:int=Form(None,description="1->yes"),
                     dealerId:int=Form(None),
                     employeeId :int=Form(None),
                     state:str=Form(None),city:str=Form(None),
                     country:str=Form(None)):
    user = deps.get_user_token(db=db,token=token)
    if user:
        # currentYear = year or datetime.now(settings.tz_IN).year
        today = datetime.now(settings.tz_IN)

        if toDatetime == None:
            toDatetime = today.replace(hour=23,minute=59,second=59)
   
        else:
            toDatetime = toDatetime.replace(hour=23,minute=59,second=59)
        if fromDateTime == None:
            fromDateTime = today.replace(day=1,month=1,hour=0,minute=0,second=0)
        else:
            fromDateTime = fromDateTime.replace(hour=0,minute=0,second=0)
        
        getTotalData = (
            db.query(
                extract('month',Lead.update_at).label('month'),
                func.count(case((Lead.lead_status_id == 1, 1))).label("open"),
                func.count(case((Lead.lead_status_id == 2, 1))).label("assigned"),
                func.count(case((Lead.lead_status_id == 3, 1))).label("demo"),
                func.count(case((Lead.lead_status_id == 4, 1))).label("quotation"),
                func.count(case((Lead.lead_status_id == 5, 1))).label("follow_up"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("order"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("close"),
                func.count(case((Lead.lead_status_id == 24, 1))).label("poc"),
                func.count(case((Lead.status == 1, 1))).label("total")
            ) ).filter(Lead.status==1)
 
      
        getTotalData = getTotalData.filter(Lead.update_at.between(fromDateTime,toDatetime))
        
        if user.user_type == 3 or dealerId:
            DealerId = user.id if user.user_type == 3 else dealerId
            getTotalData = getTotalData.filter(Lead.dealer_id == DealerId )

        if user.user_type ==4 or employeeId:
            EmployeeId = user.id if  user.user_type ==4 else employeeId
            getTotalData = getTotalData.filter(Lead.assigned_to == EmployeeId)
            
        
        if state:
            getTotalData = getTotalData.filter(Lead.states.like("%"+state+"%"))  
        if country:
            getTotalData = getTotalData.filter(Lead.country.like("%"+country+"%"))
        if city:
            getTotalData = getTotalData.filter(Lead.city.like("%"+city+"%"))

        getTotalData = getTotalData.group_by(extract('month',Lead.update_at)).all()
        
        # return getTotalData
        result_by_month={}
        formatted_result =[]
      

        # if isLineChart:
        #     if not dealerId and  not EmployeeId:
        #         print("5")
        #         return {"status":1,"msg":"Success","data":formatted_result}
                
       
    
        if getTotalData:
            for month,open,assigned,demo,quotation,follow_up,order,close,poc,total in getTotalData:

                if month not in result_by_month:
                    result_by_month[month] = {"open": 0,"assigned":0,"demo":0,"quotation":0,"follow_up":0,"order":0,"close":0}
                        
                result_by_month[month]["open"] = open
                result_by_month[month]["assigned"] = assigned
                result_by_month[month]["demo"] = demo
                result_by_month[month]['quotation'] = quotation
                result_by_month[month]["follow_up"] = follow_up
                result_by_month[month]["order"] = order
                result_by_month[month]["close"] = close
                result_by_month[month]["total"] = total
                result_by_month[month]["demo_poc"] = poc

        
        endMonth = int(toDatetime.month ) + 1 #to get up to current month data
        fromMonth = int(fromDateTime.month)
        if toDatetime.year != fromDateTime.year:
            if int(toDatetime.year) - int(fromDateTime.year) ==1:
                if int(toDatetime.month ) < int(fromDateTime.month):
                    fromMonth = fromDateTime.month
                    endMonth =13
                    formatted_result = getFormattedData(fromMonth,endMonth,result_by_month,formatted_result)

                    fromMonth = 1
                    endMonth = int(toDatetime.month ) +1
                    formatted_result = getFormattedData(fromMonth,endMonth,result_by_month,formatted_result)
                else:
                    fromMonth=1
                    endMonth =13
                    formatted_result = getFormattedData(fromMonth,endMonth,result_by_month,formatted_result)
            else:
                fromMonth = 1
                endMonth =13
                formatted_result = getFormattedData(fromMonth,endMonth,result_by_month,formatted_result)
        else:
        
            formatted_result = getFormattedData(fromMonth,endMonth,result_by_month,formatted_result)

        return {"status":1,"msg":"Success","data":formatted_result}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}
    
def getFormattedData(fromMonth,endMonth,result_by_month,formatted_result):
    for month in range(fromMonth,endMonth): # 12 Month
        if month in result_by_month:
            data = result_by_month[month]
            open  = data["open"]
            assigned = data["assigned"]
            demo =data["demo"]
            quotation = data["quotation"]
            follow_up = data["follow_up"]
            order = data["order"]
            close = data["close"]
            poc = data["demo_poc"]
            totalCount = data["total"]

        else:
            open = 0
            assigned = 0
            demo = 0
            quotation = 0
            follow_up = 0
            close = 0
            order = 0
            poc=0
            totalCount = 1 
        # totalCount = open + assigned + demo +  quotation + follow_up + close + order
        formatted_result.append({
                "month": month,
                "Open":open,
                "Assigned":assigned,
                "Demo":demo,
                "Quotation":quotation,
                "Follow up":follow_up,
                "Order":order ,
                "Close":close,
                "demo_poc":poc,
                "total":totalCount,
                "successPercentage":(order/totalCount)*100})
    return formatted_result
 

import calendar
    
@router.post("/pie_chart")
async def pieChart(db:Session = Depends(deps.get_db),
                   token:str=Form(...)
                    ,dealerId:int=Form(None),
                   employeeId:int=Form(None),state:str=Form(None),city:str=Form(None),
                    country:str=Form(None),fromDatetime:datetime=Form(None),
                   todatetime:datetime=Form(None)):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        today = datetime.now(settings.tz_IN)
        getMonth =calendar.monthrange(today.year, today.month)[1]
        if not fromDatetime:
            fromDatetime = today.replace(day=1,hour=1,minute=1,second=1)
        else:
            fromDatetime = fromDatetime.replace(hour=0,minute=0,second=0)
        if not todatetime:
            todatetime = today.replace(day=getMonth,hour=23,minute=59,second=59)
        else:
            todatetime = todatetime.replace(hour=23,minute=59,second=59)

        getTotalData = (
            db.query(
                func.count(case((Lead.lead_status_id == 1, 1))).label("open"),
                func.count(case((Lead.lead_status_id == 2, 1))).label("assigned"),
                func.count(case((Lead.lead_status_id == 3, 1))).label("demo"),
                func.count(case((Lead.lead_status_id == 4, 1))).label("quotation"),
                func.count(case((Lead.is_followup == 1, 1))).label("follow_up"),
                # func.count(case((Lead.lead_status_id == 5, 1))).label("follow_up"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("order"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("close"),
                func.count(case((Lead.lead_status_id == 17, 1))).label("invalid"),
                func.count(case((Lead.lead_status_id == 8, 1))).label("poc")
            ) ).filter(Lead.update_at.between(fromDatetime,todatetime),Lead.status == 1)
        
        getMissedLead = db.query(
                func.count(Lead.id)).filter(Lead.status == 1,
                                            # Lead.lead_status_id==5,
                                            Lead.is_followup==1,
                                            func.DATE_FORMAT(Lead.schedule_date, '%Y-%m-%d %H:%M') < (today.strftime('%Y-%m-%d %H:%M')))

        
        if user.user_type == 3 or dealerId:
            DealerId = user.id if user.user_type == 3 else dealerId
            getTotalData = getTotalData.filter(Lead.dealer_id == DealerId )
            getMissedLead = getMissedLead.filter(Lead.dealer_id == DealerId )


        if user.user_type ==4:
            getTotalData = getTotalData.filter(Lead.assigned_to == user.id )
            getMissedLead = getMissedLead.filter(Lead.assigned_to == user.id )


        if employeeId:
            getTotalData = getTotalData.filter(Lead.assigned_to == employeeId)
            getMissedLead = getMissedLead.filter(Lead.assigned_to == employeeId)

        if state:
            getAllLead = getAllLead.filter(Lead.states.like("%"+state+"%"))  
            getMissedLead = getMissedLead.filter(Lead.states.like("%"+state+"%"))  

        if country:
            getAllLead = getAllLead.filter(Lead.country.like("%"+country+"%"))
            getMissedLead = getMissedLead.filter(Lead.country.like("%"+country+"%"))

        if city:
            getAllLead = getAllLead.filter(Lead.city.like("%"+city+"%"))
            getMissedLead = getMissedLead.filter(Lead.city.like("%"+city+"%"))

        
        getTotalData = getTotalData.all()
        getMissedLead = getMissedLead.all()


        totalData = []  

        if getTotalData:
            for open,assign,demo,quotation,follow_up,order,close,invalid,poc in getTotalData:
                totalData=[ {
                    "label":"Unassigned",
                    "value":open
                },
                 {
                    "label":"demo_poc",
                    "value":poc
                },
                {
                    "label":"Assigned",
                    "value":assign
                },
                {
                    "label":"Demo",
                    "value":demo
                },
                {
                    "label":"Quotation",
                    "value":quotation
                },
                {
                    "label":"Follow Up",
                    "value":follow_up
                },
                  {
                    "label":"Missed",
                    "value":getMissedLead[0][0]
                },
                {
                    "label":"Order",
                    "value":order
                },
                {
                    "label":"Cancel",
                    "value":close
                },
                {
                    "label":"Not valid",
                    "value":invalid
                }
                ]
                
        return {"status":1,"msg":"Success","data":totalData,"total":open + demo+quotation+follow_up+order+close}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}
    
@router.post("/dealerWisePerformance")
async def dealerWisePerformance(db:Session=Depends(deps.get_db),token:str=Form(None),dealerId:int=Form(None),
                                state:str=Form(None),city:str=Form(None),district:str=Form(None),fromDatetime:datetime=Form(None),toDatetime:datetime=Form(None),page:int=1,size:int=10):
    user = deps.get_user_token(db=db,token=token)
    if user:
        today = datetime.now()
        if not fromDatetime:
            fromDatetime = today.replace(day=1,month=1,hour=0,minute=0,second=0)
        else:
            fromDatetime = fromDatetime.replace(hour=0,minute=0,second=0)
        if not toDatetime:
            toDatetime = today.replace(hour=23,minute=59,second=59)
        else:
            toDatetime = toDatetime.replace(hour=23,minute=59,second=59)

        getAllLead = db.query(Lead).filter(LeadStatus.status==1,Lead.update_at.between(fromDatetime,toDatetime))

        getAllDealer =  db.query(User.id,User.name).filter(User.status==1,User.user_type == 3)
        if dealerId:
            getAllDealer = getAllDealer.filter(User.id == dealerId)

        if state:
            getAllLead = getAllLead.filter(Lead.states.like("%"+state+"%"))  
        if city:
            getAllLead = getAllLead.filter(Lead.city.like("%"+city+"%"))


        totalCount = getAllDealer.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)
        getAllDealer = getAllDealer.order_by(User.id.desc()).limit(limit).offset(offset).all()

        dataList =[]
        for dealer in getAllDealer:
            total,order=getDealerData(db,fromDatetime,toDatetime,dealer.id)
            if total == 0 and order == 0:
                total = 1
            dataList.append({
                "Dealer":dealer.name,
                "dealer_id": dealer.id,
                "totalLead":total,
                "orderLead":order,
                "successPercentage": (order/total) *100 
  
            })
    
        data=({"page":page,"size":size,
                    "total_page":totalPage,
                    "total_count":totalCount,
                    "items":dataList})
        return ({"status":1,"msg":"Success","data":data})
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}



def getDealerData(db:Session,fromdatetime,todatetime,dealerId:int):

    getTotalData = (
            db.query(
                func.count(case((Lead.status == 1, 1))).label("all"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("order"),
            ) ).filter(Lead.update_at.between(fromdatetime,todatetime),Lead.status == 1)
        
    
    getTotalData = getTotalData.filter(Lead.dealer_id == dealerId )
    getTotalData = getTotalData.all()

    if getTotalData:
        for data in getTotalData:
            return data.all,data.order
    return 0,0
        
@router.post("/employee_pie_chart")
async def employeePieChart(db:Session = Depends(deps.get_db),
                   token:str=Form(...),
                   employeeId:int=Form(None),fromDateTime :datetime =Form(None),
                     toDatetime : datetime = Form(None),
                   page:int=1,size:int=10,
                    state:str=Form(None),city:str=Form(None)
                  ):
    
    user = deps.get_user_token(db=db,token=token)
    if user:
        todayDt = datetime.now(settings.tz_IN)
        fromDt = datetime.now(settings.tz_IN)
        toDt = datetime.now(settings.tz_IN)
        fromDate = datetime.now(settings.tz_IN).date()
        toDate = datetime.now(settings.tz_IN).date()

        if toDatetime :
            toDt = toDatetime
            toDate = toDatetime.date()
        if fromDateTime :
            fromDt = fromDateTime
            fromDate = fromDateTime.date()

        getTotalData = (
            db.query(
                func.count(case((Lead.lead_status_id == 1, 1))).label("open"),
                func.count(case((Lead.lead_status_id == 2, 1))).label("assigned"),
                func.count(case((Lead.lead_status_id == 3, 1))).label("demo"),
                func.count(case((Lead.lead_status_id == 4, 1))).label("quotation"),
                func.count(case((Lead.is_followup == 1, 1))).label("follow_up"),
                # func.count(case((Lead.lead_status_id == 5, 1))).label("follow_up"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("order"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("close"),
                func.count(case((Lead.lead_status_id == 17, 1))).label("invalid"),
                func.count(case((Lead.lead_status_id == 8, 1))).label("poc")
            ) ).filter(Lead.status == 1)
        

        if fromDateTime and toDatetime:

            getTotalData = getTotalData.filter(func.date(Lead.update_at).between(fromDate,toDate))
        elif fromDateTime:
            getTotalData = getTotalData.filter(func.date(Lead.update_at)==fromDate)
        else:
            getTotalData = getTotalData.filter(func.date(Lead.update_at)==fromDate)

      
        getMissded = db.query(
            Lead.id,
                func.count(Lead.id)).filter(Lead.status == 1,
                                            # Lead.lead_status_id==5,
                                            Lead.is_followup==1
                                           )


        if fromDateTime and toDatetime:
            getMissded = getMissded.filter(func.date(Lead.schedule_date).between(fromDate,toDate),
               Lead.schedule_date < todayDt)

        elif fromDateTime:
            getMissded = getMissded.filter(func.date(Lead.schedule_date)==fromDate,
               Lead.schedule_date < todayDt)

        else:
            getMissded = getMissded.filter(func.date(Lead.schedule_date)==fromDate,
               Lead.schedule_date < todayDt)
            

        if state:
            getTotalData = getTotalData.filter(Lead.states.like("%"+state+"%"))  
            getMissded= getMissded.filter(Lead.states.like("%"+state+"%"))  

        if city:
            getTotalData = getTotalData.filter(Lead.city.like("%"+city+"%"))
            getMissded= getMissded.filter(Lead.states.like("%"+city+"%"))  


        if employeeId:
            getTotalData = getTotalData.filter(Lead.assigned_to == employeeId)
            getMissded = getMissded.filter(Lead.assigned_to == employeeId)

        getTotalData = getTotalData.all()
        getMissded = getMissded.all()

        totalData = []  

        if getTotalData:
            for open,assign,demo,quotation,follow_up,order,close,invalid,poc in getTotalData:
                totalData=[ {
                    "label":"Unassigned",
                    "value":open
                },
                 {
                    "label":"demo_poc",
                    "value":poc
                },
                {
                    "label":"Assigned",
                    "value":assign
                },
                {
                    "label":"Demo",
                    "value":demo
                },
                {
                    "label":"Quotation",
                    "value":quotation
                },
                {
                    "label":"Follow Up",
                    "value":follow_up
                },
                  {
                    "label":"Missed",
                    "value":getMissded[0][0]
                },
                {
                    "label":"Order",
                    "value":order
                },
                {
                    "label":"Cancel",
                    "value":close
                },
                {
                    "label":"Not valid",
                    "value":invalid
                }
                ]
                
        return {"status":1,"msg":"Success","data":totalData,"total":open + demo+quotation+follow_up+order+close}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}
    


@router.post("/employee_lead_report")
async def employeeLeadReport(db:Session=Depends(deps.get_db),
                     token:str = Form(...),fromDateTime :datetime =Form(None),
                     toDatetime : datetime = Form(None),
                     employeeId :int=Form(None),
                    page:int=1,size:int=10,
                     state:str=Form(None),city:str=Form(None)
                     ):
    user = deps.get_user_token(db=db,token=token)
    
    if user:
        # currentYear = year or datetime.now(settings.tz_IN).year
        
        todayDt = datetime.now(settings.tz_IN)
        fromDt = datetime.now(settings.tz_IN)
        toDt = datetime.now(settings.tz_IN)
        fromDate = datetime.now(settings.tz_IN).date()
        toDate = datetime.now(settings.tz_IN).date()


        if toDatetime :
            toDt = toDatetime
            toDate = toDatetime.date()
        if fromDateTime :
            fromDt = fromDateTime
            fromDate = fromDateTime.date()

        
        getMissded = (
            db.query(
                Lead.assigned_to.label("user_id"),
                func.count(Lead.id).label("missed")
            )
            .filter(
                Lead.status == 1,
                Lead.is_followup == 1,
                          
            ))

        if fromDateTime and toDatetime:
            getMissded = getMissded.filter(func.date(Lead.schedule_date).between(fromDate,toDate),
               Lead.schedule_date < todayDt)

        elif fromDateTime:
            getMissded = getMissded.filter(func.date(Lead.schedule_date)==fromDate,
               Lead.schedule_date < todayDt)

        else:
            getMissded = getMissded.filter(func.date(Lead.schedule_date)==fromDate,
               Lead.schedule_date < todayDt)
            
        getMissded = getMissded.group_by(Lead.assigned_to).subquery()

        from sqlalchemy.orm import aliased

        # Alias for User table
        user_alias = aliased(User)

        getTotalData = (
            db.query(
                user_alias.user_name,
                func.count(case((Lead.lead_status_id == 1, 1))).label("open"),
                func.count(case((Lead.lead_status_id == 2, 1))).label("assigned"),
                func.count(case((Lead.lead_status_id == 3, 1))).label("demo"),
                func.count(case((Lead.lead_status_id == 4, 1))).label("quotation"),
                func.count(case((Lead.is_followup == 1, 1))).label("follow_up"),
                func.count(case((Lead.lead_status_id == 6, 1))).label("order"),
                func.count(case((Lead.lead_status_id == 7, 1))).label("close"),
                func.count(case((Lead.lead_status_id == 24, 1))).label("poc"),
                func.count(case((Lead.status == 1, 1))).label("total"),
                func.coalesce(getMissded.c.missed, 0).label("missed")
            )
            .join(user_alias, Lead.assigned_to == user_alias.id)
            .outerjoin(getMissded, user_alias.id == getMissded.c.user_id)
            .filter(Lead.status == 1)
)
        if fromDateTime and toDatetime:

            getTotalData = getTotalData.filter(func.date(Lead.update_at).between(fromDate,toDate))
        elif fromDateTime:
            getTotalData = getTotalData.filter(func.date(Lead.update_at)==fromDate)
        else:
            getTotalData = getTotalData.filter(func.date(Lead.update_at)==fromDate)

      
        # getTotalData = getTotalData.filter(func.date(Lead.update_at)==report_date)
        if state:
            getTotalData = getTotalData.filter(Lead.states.like("%"+state+"%"))  

        if city:
            getTotalData = getTotalData.filter(Lead.city.like("%"+city+"%"))

        if employeeId:
            getTotalData = getTotalData.filter(Lead.assigned_to == employeeId)

        totalCount = getTotalData.count()
        totalPage,offset,limit = get_pagination(totalCount,page,size)

        getTotalData = getTotalData.group_by(Lead.assigned_to).all()
        # getTotalData = getTotalData.order_by(Lead.id).limit(limit).offset(offset).all()


        dataList=[]
        totalCount = [row.user_name for row in getTotalData]
        totalPage = math.ceil(len(totalCount) / size)


        for row in getTotalData:
            dataList.append({"employee_name":row.user_name,
                         "open":row.open,
                         "assigned":row.assigned,
                         "demo":row.demo,
                         "quotation":row.quotation,
                         "follow_up":row.follow_up,
                         "order":row.order,
                         "close":row.close,
                         "missed":row.missed,
                         "total":row.total,
                         "demo_poc":row.poc,
                         })
        start = (page - 1) * size
        end = start + size
        dataListPage = dataList[start:end]
        data=({"page":page,"size":size,
            "total_page":totalPage,
            "total_count":len(totalCount),
            "items":dataListPage})
        


        return {"status":1,"msg":"Success","data":data}
    else:
        return {"status":-1,"msg":"Sorry your login session expires.Please login again."}