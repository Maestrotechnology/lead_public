from fastapi import APIRouter
from .endpoints import login,follow_up,import_lead,user,industry,lead,dashboard,dropdown,masters,reports,media,lead_media

api_router = APIRouter()

api_router.include_router(login.router, tags=["Login"])
api_router.include_router(follow_up.router, tags=["FollowUp"])


api_router.include_router(import_lead.router, tags=["ImportLead"])


api_router.include_router(lead_media.router, tags=["LeadMedia"])


api_router.include_router(user.router ,prefix="/user", tags=["User"])

api_router.include_router(industry.router ,prefix="/industry", tags=["Industry"])

api_router.include_router(lead.router ,prefix="/lead", tags=["Lead"])

api_router.include_router(reports.router ,prefix="/reports", tags=["Lead"])

api_router.include_router(dashboard.router ,prefix="/dashboard", tags=["Dashboard"])

api_router.include_router(dropdown.router ,prefix="/dropdown", tags=["Dropdown"])

api_router.include_router(masters.router ,prefix="/masters", tags=["Masters"])

api_router.include_router(media.router ,prefix="/media", tags=["Media"])



