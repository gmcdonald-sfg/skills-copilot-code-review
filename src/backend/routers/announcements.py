"""
Announcements endpoints for the High School Management System API
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from bson import ObjectId
import datetime

from ..database import announcements_collection, teachers_collection

router = APIRouter(
    prefix="/announcements",
    tags=["announcements"]
)


@router.get("/active")
def get_active_announcements() -> List[Dict[str, Any]]:
    """Get all announcements that are currently active (not expired)"""
    now = datetime.datetime.now()
    
    announcements = list(announcements_collection.find(
        {
            "expiration_date": {"$gte": now}
        }
    ).sort("created_at", -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
    
    return announcements


@router.get("/all")
def get_all_announcements(username: str) -> List[Dict[str, Any]]:
    """Get all announcements - only accessible to signed-in users"""
    # Verify user is logged in
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    announcements = list(announcements_collection.find().sort("created_at", -1))
    
    # Convert ObjectId to string for JSON serialization
    for announcement in announcements:
        announcement["_id"] = str(announcement["_id"])
    
    return announcements


@router.post("/create")
def create_announcement(
    username: str,
    title: str,
    message: str,
    expiration_date: str,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new announcement - only accessible to signed-in users"""
    # Verify user is logged in
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        # Parse dates (expected format: YYYY-MM-DD or ISO format)
        exp_date = datetime.datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
        
        start = None
        if start_date:
            start = datetime.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        else:
            start = datetime.datetime.now()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format (YYYY-MM-DD or ISO datetime)")
    
    announcement = {
        "title": title,
        "message": message,
        "start_date": start,
        "expiration_date": exp_date,
        "created_by": username,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now()
    }
    
    result = announcements_collection.insert_one(announcement)
    announcement["_id"] = str(result.inserted_id)
    
    return announcement


@router.put("/update/{announcement_id}")
def update_announcement(
    username: str,
    announcement_id: str,
    title: Optional[str] = None,
    message: Optional[str] = None,
    expiration_date: Optional[str] = None,
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """Update an announcement - only accessible to signed-in users"""
    # Verify user is logged in
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        obj_id = ObjectId(announcement_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    # Check if announcement exists
    announcement = announcements_collection.find_one({"_id": obj_id})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    # Prepare update data
    update_data = {
        "updated_at": datetime.datetime.now()
    }
    
    if title:
        update_data["title"] = title
    if message:
        update_data["message"] = message
    if expiration_date:
        try:
            update_data["expiration_date"] = datetime.datetime.fromisoformat(expiration_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid expiration date format")
    if start_date:
        try:
            update_data["start_date"] = datetime.datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start date format")
    
    announcements_collection.update_one(
        {"_id": obj_id},
        {"$set": update_data}
    )
    
    # Return updated announcement
    updated = announcements_collection.find_one({"_id": obj_id})
    updated["_id"] = str(updated["_id"])
    
    return updated


@router.delete("/delete/{announcement_id}")
def delete_announcement(username: str, announcement_id: str) -> Dict[str, Any]:
    """Delete an announcement - only accessible to signed-in users"""
    # Verify user is logged in
    teacher = teachers_collection.find_one({"_id": username})
    if not teacher:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        obj_id = ObjectId(announcement_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid announcement ID")
    
    # Check if announcement exists
    announcement = announcements_collection.find_one({"_id": obj_id})
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    announcements_collection.delete_one({"_id": obj_id})
    
    return {"message": "Announcement deleted successfully", "id": announcement_id}
