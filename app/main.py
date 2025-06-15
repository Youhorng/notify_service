from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import database functions
from app.db.notifications import connect_to_mongodb, close_db_connection

# Import routers
from app.routers.notification_routers import router as notification_router

# Create FastAPI application
app = FastAPI(
    title="Credit Card Fraud Notification Service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register event handlers
@app.on_event("startup")
async def startup_event():
    """Connect to database when app starts"""
    await connect_to_mongodb()
    logging.info("Notification Service started")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection when app shuts down"""
    await close_db_connection()

# Add router
app.include_router(notification_router)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Credit Card Fraud Notification Service",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "ok"}

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5005))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)