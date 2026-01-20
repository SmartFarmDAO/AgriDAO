"""
Dispute resolution API endpoints.
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field

from ..models import User, DisputeStatus, DisputeType
from ..deps import get_current_user
from ..services.dispute_service import DisputeService


router = APIRouter()
dispute_service = DisputeService()


class CreateDisputeRequest(BaseModel):
    """Request model for creating a dispute."""
    order_id: int
    dispute_type: DisputeType
    subject: str = Field(..., max_length=255)
    description: str = Field(..., max_length=2000)
    evidence_urls: Optional[List[str]] = Field(default_factory=list)


class AddDisputeMessageRequest(BaseModel):
    """Request model for adding a message to a dispute."""
    message: str = Field(..., max_length=2000)
    attachments: Optional[List[str]] = Field(default_factory=list)


class UpdateDisputeStatusRequest(BaseModel):
    """Request model for updating dispute status (admin only)."""
    status: DisputeStatus
    resolution: Optional[str] = Field(None, max_length=2000)


class AdminDisputeMessageRequest(BaseModel):
    """Request model for admin messages."""
    message: str = Field(..., max_length=2000)
    is_internal: bool = Field(default=False)
    attachments: Optional[List[str]] = Field(default_factory=list)


@router.post("/disputes")
def create_dispute(
    request: CreateDisputeRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new dispute for an order."""
    
    try:
        result = dispute_service.create_dispute(
            order_id=request.order_id,
            filed_by=current_user.id,
            dispute_type=request.dispute_type,
            subject=request.subject,
            description=request.description,
            evidence_urls=request.evidence_urls
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create dispute: {str(e)}")


@router.get("/disputes")
def get_my_disputes(
    status: Optional[List[DisputeStatus]] = Query(None, description="Filter by dispute status"),
    limit: int = Query(20, ge=1, le=100, description="Number of disputes to return"),
    offset: int = Query(0, ge=0, description="Number of disputes to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get current user's disputes."""
    
    try:
        result = dispute_service.get_user_disputes(
            user_id=current_user.id,
            status_filter=status,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve disputes: {str(e)}")


@router.get("/disputes/{dispute_id}")
def get_dispute_details(
    dispute_id: int,
    current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific dispute."""
    
    try:
        result = dispute_service.get_dispute_details(
            dispute_id=dispute_id,
            user_id=current_user.id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dispute: {str(e)}")


@router.post("/disputes/{dispute_id}/messages")
def add_dispute_message(
    dispute_id: int,
    request: AddDisputeMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Add a message to a dispute."""
    
    try:
        result = dispute_service.add_dispute_message(
            dispute_id=dispute_id,
            sender_id=current_user.id,
            message=request.message,
            attachments=request.attachments
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add message: {str(e)}")


# Admin-specific endpoints
@router.get("/admin/disputes")
def get_admin_disputes(
    status: Optional[List[DisputeStatus]] = Query(None, description="Filter by dispute status"),
    priority: Optional[List[int]] = Query(None, description="Filter by priority (1-5)"),
    limit: int = Query(50, ge=1, le=100, description="Number of disputes to return"),
    offset: int = Query(0, ge=0, description="Number of disputes to skip"),
    current_user: User = Depends(get_current_user)
):
    """Get all disputes for admin review."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = dispute_service.get_admin_disputes(
            admin_id=current_user.id,
            status_filter=status,
            priority_filter=priority,
            limit=limit,
            offset=offset
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve admin disputes: {str(e)}")


@router.put("/admin/disputes/{dispute_id}/status")
def update_dispute_status(
    dispute_id: int,
    request: UpdateDisputeStatusRequest,
    current_user: User = Depends(get_current_user)
):
    """Update dispute status (admin only)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = dispute_service.update_dispute_status(
            dispute_id=dispute_id,
            new_status=request.status,
            admin_id=current_user.id,
            resolution=request.resolution
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update dispute status: {str(e)}")


@router.post("/admin/disputes/{dispute_id}/messages")
def add_admin_dispute_message(
    dispute_id: int,
    request: AdminDisputeMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """Add an admin message to a dispute (can be internal)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = dispute_service.add_dispute_message(
            dispute_id=dispute_id,
            sender_id=current_user.id,
            message=request.message,
            is_internal=request.is_internal,
            attachments=request.attachments
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add admin message: {str(e)}")


@router.post("/admin/disputes/auto-escalate")
def auto_escalate_disputes(
    current_user: User = Depends(get_current_user)
):
    """Manually trigger auto-escalation of disputes (admin only)."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = dispute_service.auto_escalate_disputes()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to auto-escalate disputes: {str(e)}")


@router.get("/admin/disputes/analytics")
def get_dispute_analytics(
    current_user: User = Depends(get_current_user)
):
    """Get dispute analytics for admin dashboard."""
    
    # Check if user is admin
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # This would be implemented to provide analytics
    # For now, return a placeholder
    return {
        "total_disputes": 0,
        "open_disputes": 0,
        "resolved_disputes": 0,
        "average_resolution_time": 0,
        "disputes_by_type": {},
        "disputes_by_priority": {},
        "message": "Dispute analytics not yet implemented"
    }