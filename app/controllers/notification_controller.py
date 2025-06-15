from ..db.notifications import (
    save_notification,
    get_notification_by_txn_id,
    update_notification,
    get_notifications
)
from ..services.telegram_service import telegram_service
import logging 
from datetime import datetime 


"""
Process a fraud notification:
1. Save notification to database with "pending" status
2. Send notification to Telegram
3. Update notification status based on result
"""
async def send_fraud_notification(data):
    try:
        # Check if notification already exists
        existing = await get_notification_by_txn_id(data.get("transaction_number"))

        if existing:
            return {
                "success":True,
                "message": "Notification already exists for this transaction.",
                "notification_id": existing["_id"],
                "status": existing["status"]
            }

        # 1. Create and save notification with pending status 
        notification = {
            "transaction_number": data["transaction_number"],
            "transaction_amount": data["transaction_amount"],
            "fraud_probability": data["fraud_probability"],
            "category": data.get("category"),
            "merchant": data.get("merchant"),
            "is_nighttime": data.get("is_nighttime"),
            "status": "pending",
            "created_at": datetime.now()
        }
        
        saved = await save_notification(notification)

        # 2. Send notification to Telegram
        try:
            telegram_result = await telegram_service.send_fraud_alert(data)     

            # 3. Update notification status based on Telegram result
            if telegram_result.get("success"):
                # Success -> update status to "sent"
                await update_notification(saved["_id"], {
                    "status": "sent",
                    "sent_at": datetime.now(),
                    "message_id": telegram_result.get("message_id"),
                    "content": telegram_result.get("content")
                })  

                return {
                    "success": True,
                    "message": "Notification sent successfully.",
                    "notification_id": saved["_id"],
                    "status": "sent"
                }
            else:
                # Failure - update status to "failed"
                await update_notification(saved["_id"], {
                    "status": "failed",
                    "error": telegram_result.get("error", "Unknown error"),
                    "failed_at": datetime.now()
                })
                
                return {
                    "success": False,
                    "message": "Failed to send notification",
                    "notification_id": saved["_id"],
                    "status": "failed",
                    "error": telegram_result.get("error", "Unknown error")
                }
            
        except Exception as e:
            # Exception during sending - update status to "failed"
            await update_notification(saved["_id"], {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now()
            })
            
            logging.error(f"Error sending notification: {str(e)}")
            return {
                "success": False,
                "message": "Error sending notification",
                "notification_id": saved["_id"],
                "status": "failed",
                "error": str(e)
            }
            
    except Exception as e:
        logging.error(f"Error processing notification: {str(e)}")
        return {
            "success": False,
            "message": "Error processing notification",
            "error": str(e)
        }
    
"""
Get the status of a notification by ID or transaction ID.
"""
async def get_notification_status(id):
    try:
        notification = await get_notification_by_txn_id(id)
        
        if not notification:
            return None
        
        # Return a simplified response with just the essential information
        return {
            "notification_id": notification["_id"],
            "transaction_number": notification["transaction_number"],
            "status": notification["status"],
            "created_at": notification.get("created_at"),
            "sent_at": notification.get("sent_at"),
            "error": notification.get("error"),
            "fraud_probability": notification.get("fraud_probability"),
            "transaction_amount": notification.get("transaction_amount"),
            "message_id": notification.get("message_id")
        }
    
    except Exception as e:
        logging.error(f"Error getting notification status: {str(e)}")
        return None


"""
List all notification with pagination
"""
async def list_all_notifications(page=1, limit=10):
    try:
        result = await get_notifications(page, limit)
        
        # Simplify the response format for the API
        simplified_notifications = []
        
        for notification in result["notifications"]:
            simplified_notifications.append({
                "notification_id": notification["_id"],
                "transaction_number": notification["transaction_number"],
                "status": notification["status"],
                "created_at": notification.get("created_at"),
                "sent_at": notification.get("sent_at")
            })
        
        return {
            "success": True,
            "notifications": simplified_notifications,
            "total": result["total"],
            "page": result["page"],
            "limit": result["limit"],
            "pages": result["pages"]
        }
    
    except Exception as e:
        logging.error(f"Error listing notifications: {str(e)}")
        return {
            "success": False,
            "message": "Error listing notifications",
            "error": str(e),
            "notifications": []
        }