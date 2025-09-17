"""
Privacy compliance API endpoints for GDPR, CCPA, and user privacy rights.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from app.core.privacy import privacy_manager
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/privacy", tags=["privacy"])


@router.get("/consent", response_model=Dict[str, Any])
async def get_user_consent(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current privacy consent status for authenticated user.
    
    Returns:
        Dictionary containing consent status for all data processing types
    """
    consent = await privacy_manager.get_user_consent(current_user.id)
    
    return {
        "user_id": current_user.id,
        "consent": consent,
        "consent_types": privacy_manager.consent_types
    }


@router.post("/consent")
async def update_consent(
    request: Request,
    consent_type: str,
    granted: bool,
    current_user: User = Depends(get_current_user)
) -> Dict[str, str]:
    """
    Update privacy consent for authenticated user.
    
    Args:
        consent_type: Type of consent to update
        granted: Whether consent is granted (true/false)
    
    Returns:
        Success message
    """
    if consent_type not in privacy_manager.consent_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid consent type. Valid types: {list(privacy_manager.consent_types.keys())}"
        )
    
    # Get request metadata
    ip_address = request.client.host
    user_agent = request.headers.get("user-agent", "unknown")
    
    success = await privacy_manager.record_consent(
        user_id=current_user.id,
        consent_type=consent_type,
        granted=granted,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update consent")
    
    return {
        "message": f"Consent updated for {consent_type}",
        "consent_type": consent_type,
        "granted": granted
    }


@router.get("/export")
async def export_user_data(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Export all user data for GDPR/CCPA data portability.
    
    Returns:
        Complete user data export
    """
    data = await privacy_manager.export_user_data(current_user.id)
    
    if "error" in data:
        raise HTTPException(status_code=500, detail=data["error"])
    
    return {
        "user_id": current_user.id,
        "export_timestamp": data.get("timestamp", "unknown"),
        "data": data
    }


@router.post("/delete")
async def delete_user_data(
    deletion_scope: str = "full",
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Request deletion of user data (GDPR/CCPA right to deletion).
    
    Args:
        deletion_scope: Scope of deletion ("full", "personal", "activity")
    
    Returns:
        Deletion confirmation
    """
    valid_scopes = ["full", "personal", "activity"]
    if deletion_scope not in valid_scopes:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid deletion scope. Valid scopes: {valid_scopes}"
        )
    
    result = await privacy_manager.delete_user_data(
        user_id=current_user.id,
        deletion_scope=deletion_scope
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.post("/request/{request_type}")
async def process_data_request(
    request_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process user data requests (access, portability, correction).
    
    Args:
        request_type: Type of data request ("access", "portability", "correction")
    
    Returns:
        Request processing status
    """
    valid_types = ["access", "portability", "correction"]
    if request_type not in valid_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid request type. Valid types: {valid_types}"
        )
    
    result = await privacy_manager.process_data_request(
        user_id=current_user.id,
        request_type=request_type
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/policy", response_model=Dict[str, Any])
async def get_privacy_policy() -> Dict[str, Any]:
    """
    Get current privacy policy information.
    
    Returns:
        Current privacy policy details
    """
    policy = privacy_manager.get_privacy_policy()
    
    return {
        "version": policy.version,
        "effective_date": policy.effective_date.isoformat(),
        "last_updated": policy.last_updated.isoformat(),
        "sections": policy.sections,
        "consent_types": privacy_manager.consent_types
    }


@router.get("/summary")
async def get_privacy_summary(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get comprehensive privacy summary for authenticated user.
    
    Returns:
        Complete privacy overview including consent, data requests, and rights
    """
    consent = await privacy_manager.get_user_consent(current_user.id)
    
    return {
        "user_id": current_user.id,
        "consent_status": consent,
        "privacy_rights": {
            "right_to_access": True,
            "right_to_portability": True,
            "right_to_correction": True,
            "right_to_deletion": True,
            "right_to_object": True,
            "right_to_restrict_processing": True
        },
        "data_retention": {
            "account_data": "Indefinite (until account deletion)",
            "transaction_data": "7 years (tax purposes)",
            "activity_logs": "1 year",
            "consent_records": "Indefinite (legal requirement)"
        },
        "contact": {
            "privacy_officer": "privacy@agridao.com",
            "data_protection_officer": "dpo@agridao.com"
        }
    }


@router.post("/validate-consent")
async def validate_consent(
    consent_type: str,
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Validate if user has given consent for specific data processing.
    
    Args:
        consent_type: Type of consent to validate
    
    Returns:
        Consent validation result
    """
    if consent_type not in privacy_manager.consent_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid consent type. Valid types: {list(privacy_manager.consent_types.keys())}"
        )
    
    has_consent = privacy_manager.validate_consent(current_user.id, consent_type)
    
    return {
        "consent_type": consent_type,
        "has_consent": has_consent,
        "description": privacy_manager.consent_types[consent_type]
    }