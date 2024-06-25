from fastapi import APIRouter, Depends, Form,UploadFile,File
from sqlalchemy.orm import Session
from app.models import *
from app.api import deps
from app.core.config import settings
from datetime import datetime
from app.utils import *
from sqlalchemy import *
import xlsxwriter

router = APIRouter()

def check_headers(data,headers):
    value=0
    for no,head in enumerate(data):

        if head not in headers and not str(head).startswith("Unnamed:"):
            value=1
            break
    return no,head,value

@router.post("/importLead")
async def importLead(
        db: Session = Depends(deps.get_db), *,
        token:str = Form(...),
        uploaded_file:UploadFile=File(...,description="xls,xlsx,csv,ods")):
    
    user = deps.get_user_token(db=db, token=token)

    if user:

        allLeadData = []
        file_extension = uploaded_file.filename.split(".")[1]
        if not file_extension in ["xls", "xlsx", "csv", "ods"]:
            return {"status":0,"msg":"Invalid File Format"}
        
        leadDetails = await uploaded_file.read()    
        
        base_dir = settings.BASE_UPLOAD_FOLDER+"/upload_files"
        dt = str(int(datetime.utcnow().timestamp()))

        try:
            os.makedirs(base_dir, mode=0o777, exist_ok=True)
        except OSError as e:
            sys.exit("Can't create {dir}: {err}".format(
                dir=base_dir, err=e))
        
        file_path = f"{base_dir}/leadRecords{dt}.xlsx"
        with open(f"{file_path}", 'wb') as f:
            f.write(leadDetails)

        import pandas as pd

        excel_data = pd.read_excel(file_path)
    
        data = pd.DataFrame(excel_data)

        leadCol = data.columns.to_list()
        
        # headers = ["name","phone",
        #            "company_name",
        #            "address","customer_category",
        #            "enquiry_type","requirements","schedule_date",
        #            "approximate_amount","description","received_date"]

        

        # no,head,value = check_headers(leadCol,headers) 
        # if value==1:
        #     return {"status":0,"msg":f"{head} is Invalid header"}


        for index, row in data.iterrows():
            index=index+1

            name = str(row["Contact_Person_Name"])
            phone = str(row["Contact Number"])if not pd.isna(row["Contact Number"]) else None
            company_name = str(row["Company"]) if not pd.isna(row["Company"]) else None
            address = str(row["City"])
            email = str(row["Email"])
            remarks = str(row["Designation"])
            # customer_category = str(row["customer_category"])  if not pd.isna(row["customer_category"]) else None
            # enquiry_type = str(row["enquiry_type"])   if not pd.isna(row["enquiry_type"]) else None
            # requirements_id = str(row["requirements"]) 
            # schedule_date = row["schedule_date"] if not pd.isna(row["schedule_date"]) else None
            # approximate_amount = str(row["approximate_amount"]) if not pd.isna(row["approximate_amount"]) else None
            # description = str(["description"])  if not pd.isna(row["description"]) else None
            # receivedDate = row["received_date"] if not pd.isna(row["received_date"]) else None
            isNew =0


            assignedUser = None
            enquiryId = None
            CustomerCategoryId = None

            getAllUsers = db.query(User).filter(User.status == 1)


            dealerId = None
            leadStatusID = 1

            if user.user_type == 3:
                dealerId = user.id
                                
            elif user.user_type == 4:
                dealerId = user.dealer_id if user.dealer_id else None
                assignedUser = user.id
                leadStatusID = 2

            
            # if deps.contains_emoji(name):
            #     return {"status":0,"msg":f"row {index} - Emojis are not allowed to use in name."}
            # if company_name:
            #     if deps.contains_emoji(company_name):
            #         return {"status":0,"msg":f"row {index} - Emojis are not allowed to use compnay name."}


            if user.user_type != 4:
                if not assignedUser :
                    assignedUser = None
                else:
                    checkUser = getAllUsers.filter(User.id == assignedUser,
                                                    User.user_type==4).first()
                    if not checkUser:
                        return {"status":0,"msg":f"row {index} - No employee record found."}
                    else:
                        assignedUser = assignedUser
                        leadStatusID = 2
        
            checkuser = db.query(User).filter(User.status == 1)
 
            checkMobile = checkuser.filter(or_(User.phone==phone,
                                                    User.alternative_number ==phone,
                                                    User.whatsapp_no == phone)).first()
        

            today = datetime.now(settings.tz_IN).date()

         

            allLeadData.append({"name":name,
            "company_name":company_name,
            "phone":phone,
            "address":address,
            "email":email,
            "remarks":remarks,
            # "customer_category":CustomerCategoryId,
           "enquiry_type":1,
            "dealer":91,
        #    "requirements":requirements_id,
            # "schedule_date":schedule_date,
            # "approximate_amount":approximate_amount,
            # "receivedDate":receivedDate,
            "leadStatusId":leadStatusID,
            # "assignedTo":3,
            # "description":description,
            "isNew":isNew})
            print(name)
            isNew=0

        for data in allLeadData:

            # if data["isNew"] !=1:

            createNewUser = User(
                user_type =5,
                name = data["name"],
                phone = data["phone"],
                address = data["address"],
                created_at = datetime.now(settings.tz_IN),
                status =1,
                company_name = data["company_name"],
                is_active = 1
                )

            db.add(createNewUser)
            db.commit()

            customer = createNewUser.id
        # else:
        #     customer = data["customer"]

            today = datetime.now(settings.tz_IN)
            createNewLead = Lead(
                name = data["name"],
                customer_id = customer ,
                company_name = data["company_name"],
                lead_code =0,
                phone = data["phone"],
                address =data["address"],
                # customer_category_id =data["customer_category"],
                enquiry_type_id = data["enquiry_type"],
                assigned_to=114,
                # requirements_id = data["requirements"],
                # approximate_amount =data["approximate_amount"],
                lead_status_id = 1,
                dealer_id = data["dealer"],
                # received_at = data["receivedDate"] ,
                is_active = 0,
                # comments_description = data["description"],
                created_t = today,
                update_at = today,
                is_valid = 1,
                status = 1,
                # schedule_date = data["schedule_date"] 
                )
            
            db.add(createNewLead)
            db.commit()

            newLeadName = "Lead"+str(createNewLead.id)
            createNewLead.lead_code = newLeadName
            db.commit()

            comment = "Created" 
            # if schedule_date:
            #     comment = f"Created and Schedule at {schedule_date}"
        
            createLeadHistory =  LeadHistory(
                lead_id = createNewLead.id,
                leadStatus = "Unassigned" if data["leadStatusId"] == 1 else "Assigned" if data["leadStatusId"] == 2 else "Not valid",
                lead_status_id = data["leadStatusId"],
                changedBy = user.id,
                created_at = today,
                comment =comment,
                status=1   )
            db.add(createLeadHistory)
            db.commit()

        return {"status":1,"msg":"Successfully Created"}

    else:
        return {
            "status": -1,
            "msg": "Sorry! your login session expired. please login again.",
        }
    