from pydantic import BaseModel, Field, validator # type: ignore
from typing import Optional, Dict, Any, List
from datetime import datetime

# Request Schema - for incoming notification requests
class NotificationRequest(BaseModel):
    transaction_number: str = Field(..., description="Unique identifier for the transaction")
    transaction_amount: float = Field(..., description="Amount of the transaction")
    fraud_probability: float = Field(..., ge=0, le=1, description="Fraud probability score (0-1)")
    is_nighttime: Optional[bool] = Field(None, description="True if the transaction is made at night, False otherwise")
    category: Optional[str] = Field(None, description="Merchant category")
    transaction_location: Optional[str] = Field(None, description="Location of the transaction")
    job: Optional[str] = Field(None, description="Job of the cardholder")
    state: Optional[str] = Field(None, description="State where the transaction occurred")
    
    @validator('transaction_number')
    def transaction_id_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('transaction_number cannot be empty')
        return v
    
    @validator('transaction_amount')
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('transaction_amount must be greater than 0')
        return v

# Response schema for notifications
class NotificationBase(BaseModel):
    notification_id: str = Field(..., description="Notification database ID")
    transaction_number: str = Field(..., description="Transaction ID")
    status: str = Field(..., description="Notification status (pending, sent, failed)")
    created_at: datetime = Field(..., description="When the notification was created")
    
    class Config:
        schema_extra = {
            "example": {
                "notification_id": "64a82c3e9b72f5d8e9f82c31",
                "transaction_number": "TX123456789",
                "status": "sent",
                "created_at": "2023-10-15T14:30:00.000Z"
            }
        }


class NotificationDetail(NotificationBase):
    sent_at: Optional[datetime] = Field(None, description="When the notification was sent")
    error: Optional[str] = Field(None, description="Error message if failed")
    fraud_probability: Optional[float] = Field(None, description="Fraud probability score (0-1)")
    transaction_amount: Optional[float] = Field(None, description="Amount of the transaction")
    message_id: Optional[str] = Field(None, description="Telegram message ID")
    
    class Config:
        schema_extra = {
            "example": {
                "notification_id": "64a82c3e9b72f5d8e9f82c31",
                "transaction_id": "TX123456789",
                "status": "sent",
                "created_at": "2023-10-15T14:30:00.000Z",
                "sent_at": "2023-10-15T14:30:05.000Z",
                "fraud_probability": 0.95,
                "transaction_amount": 1299.99,
                "message_id": "12345678"
            }
        }
        

class NotificationResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the notification was successfully sent")
    message: str = Field(..., description="Message indicating the status of the notification")
    notification_number: Optional[str] = Field(None, description="Notification ID")
    status: Optional[str] = Field(None, description="Notification status")
    error: Optional[str] = Field(None, description="Error message if any")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Notification sent successfully",
                "notification_number": "64a82c3e9b72f5d8e9f82c31",
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