from fastapi import APIRouter, HTTPException, Query, Path
from ..models.schemas import (
    NotificationRequest,
    NotificationResponse,
    NotificationDetail,
    PaginatedNotifications
)
from ..controllers.notification_controller import (
    send_fraud_notification,
    get_notification_status,
    list_all_notifications
)

# Create Router
router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@router.post("/send", response_model=NotificationResponse)
async def send_notification(request: NotificationRequest):
    # Send a fraud notification to Telegram 
    result = await send_fraud_notification(request.dict())

    if not result["success"] and "error" in result:
        if "already exists" in result.get("message", ""):
            # Not really an error, just informational
            return result
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    return result   


@router.get("/status/{id}", response_model=NotificationDetail)
async def check_status(id: str = Path(..., description="Notification ID or Transaction ID")):
    """Check the status of a notification"""
    result = await get_notification_status(id)
    
    if not result:
        raise HTTPException(status_code=404, detail=f"Notification not found with ID: {id}")
    
    return result


@router.get("/", response_model=PaginatedNotifications)
async def list_notifications(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """List all notifications with pagination"""
    result = await list_all_notifications(page, limit)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result