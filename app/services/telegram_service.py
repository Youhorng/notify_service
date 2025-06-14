from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# Request schema for incoming notification requests 
class NotificationRequests(BaseModel):
    transaction_id: str = Field(..., description="Unique identifier for the transaction")
    is_fraud: bool = Field(..., description="Prediction result: '1' for fraud, '0' for not fraud")
    label: str = Field(..., description="Label indicating if the transaction is fraudulent or not")
    fraud_probability: float = Field(..., description="Probability of the transaction being fraudulent")

    @validator("transaction_id")
    def transaction_id_must_not_be_empty(cls, v):
        if not v:
            raise ValueError("Transaction ID must not be empty")
        return v
    

# Response schema for notifications
class NotificationBase(BaseModel):
    notification_id: str = Field(..., description="Notification database ID")
    transaction_id: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Notification status (pending, sent, failed)")
    created_at: datetime = Field(..., description="When the notification was created")
    
    class Config:
        schema_extra = {
            "example": {
                "notification_id": "64a82c3e9b72f5d8e9f82c31",
                "transaction_id": "TX123456789",
                "status": "sent",
                "created_at": "2023-10-15T14:30:00.000Z"
            }
        }


class NotificationResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the notification was successfully sent")
    message: str = Field(..., description="Message indicating the status of the notification")
    notification_id: Optional[str] = Field(None, description="Notification ID")
    status: Optional[str] = Field(None, description="Notification status")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Notification sent successfully",
                "notification_id": "64a82c3e9b72f5d8e9f82c31",
                "status": "sent"
            }
        }


class PaginatedNotifications(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    notifications: List[NotificationBase] = Field(..., description="List of notifications")
    total: int = Field(..., description="Total number of notifications")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "notifications": [
                    {
                        "notification_id": "64a82c3e9b72f5d8e9f82c31",
                        "transaction_id": "TX123456789",
                        "status": "sent",
                        "created_at": "2023-10-15T14:30:00.000Z"
                    }
                ],
                "total": 42,
                "page": 1,
                "limit": 10,
                "pages": 5
            }
        }