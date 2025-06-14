from motor.motor_asyncio import AsyncIOMotorClient # type: ignore
from bson import ObjectId # type: ignore
from datetime import datetime 
import os 
import logging 
from dotenv import load_dotenv # type: ignore

# Load environment variables from .env file
load_dotenv()

# MongoDB connection string
MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DB = os.getenv("MONGODB_DB")

# MongoDB connection
client = None
db = None

# Connect to MongoDB database
async def connect_to_mongodb():
    global client, db
    
    try:
        # Connect MongoDB
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client[MONGODB_DB]

        # Create index for faster lookups 
        await db.notifications.create_index("transaction_id", unique=True)

        logging.info("Connected to MongoDB")

    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
        raise e


# Clost the database connection
async def close_db_connection():
    global client
    
    if client:
        client.close()
        logging.info("Closed MongoDB connection")
    else:
        logging.warning("No MongoDB connection to close")

# Save notification to the database
async def save_notification(notification_data):
    global db
    if db is None:
        await connect_to_mongodb()
    
    try:
        # Add timestamp
        if "created_at" not in notification_data:
            notification_data["created_at"] = datetime.now()
        
        # Insert notification
        result = await db.notifications.insert_one(notification_data)   

        # Add MongoDB ID to the notification data 
        notification_data["_id"] = str(result.inserted_id)
        
        return notification_data
    
    except Exception as e:
        logging.error(f"Failed to save notification: {str(e)}")
        raise e
    
# Get notification by transaction ID
async def get_notification_by_txn_id(id):
    global db
    if db is None:
        await connect_to_mongodb()
    
    notification = None
    
    try:
        # First try to find by MongoDB ObjectId
        if len(id) == 24:  # MongoDB ObjectId is 24 hex chars
            try:
                notification = await db.notifications.find_one({"_id": ObjectId(id)})
            except:
                pass
        
        # If not found or not a valid ObjectId, try by transaction_id
        if not notification:
            notification = await db.notifications.find_one({"transaction_id": id})
        
        # Convert ObjectId to string for easier handling
        if notification:
            notification["_id"] = str(notification["_id"])
        
        return notification
    
    except Exception as e:
        logging.error(f"Error getting notification: {str(e)}")
        return None


# Update notification in database
async def update_notification(id, update_data):
    global db
    if db is None:
        await connect_to_mongodb()
    
    try:
        # Add updated_at timestamp
        if "updated_at" not in update_data:
            update_data["updated_at"] = datetime.now()
        
        # Try to update by MongoDB ObjectId first
        if len(id) == 24:  # Check if it looks like an ObjectId
            try:
                result = await db.notifications.update_one(
                    {"_id": ObjectId(id)},
                    {"$set": update_data}
                )
                
                if result.modified_count > 0:
                    return await get_notification_by_txn_id(id)
            except Exception as e:
                logging.error(f"Error updating by ObjectId: {str(e)}")
        
        # Try updating by transaction_id
        result = await db.notifications.update_one(
            {"transaction_id": id},
            {"$set": update_data}
        )
        
        if result.modified_count > 0:
            return await get_notification_by_txn_id(id)
        
        logging.warning(f"No notification found to update with ID: {id}")
        return None
        
    except Exception as e:
        logging.error(f"Failed to update notification: {str(e)}")
        return None
    

# Get all notifications with pagination
async def get_notifications(page=1, limit=10):
    """Get all notifications with pagination"""
    global db
    if db is None:
        await connect_to_mongodb()
    
    try:
        # Calculate skip value for pagination
        skip = (page - 1) * limit
        
        # Get notifications with pagination, sorted by newest first
        cursor = db.notifications.find().sort("created_at", -1).skip(skip).limit(limit)
        notifications = await cursor.to_list(length=limit)
        
        # Convert ObjectIds to strings
        for notification in notifications:
            notification["_id"] = str(notification["_id"])
        
        # Count total documents for pagination metadata
        total_count = await db.notifications.count_documents({})
        
        return {
            "notifications": notifications,
            "total": total_count,
            "page": page,
            "limit": limit,
            "pages": (total_count + limit - 1) // limit  # Ceiling division
        }
    
    except Exception as e:
        logging.error(f"Error getting notifications: {str(e)}")
        return {
            "notifications": [],
            "total": 0,
            "page": page,
            "limit": limit,
            "pages": 0
        }