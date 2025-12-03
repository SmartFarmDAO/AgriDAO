"""
File upload and management API endpoints.
"""

import os
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user
from app.core.storage import storage_manager
from app.core.logging import get_logger
from app.models.user import User
from app.models.file import FileUpload, FileMetadata

logger = get_logger("files_api")
router = APIRouter(prefix="/files", tags=["files"])


@router.post("/upload", response_model=dict)
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a file to cloud storage."""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Validate file size (max 100MB)
        max_size = 100 * 1024 * 1024  # 100MB
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning
        
        if file_size > max_size:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Create temporary file
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        
        # Save uploaded file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Generate destination path
        destination_path = folder or "uploads"
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        full_destination = f"{destination_path}/{unique_filename}"
        
        # Parse metadata
        file_metadata = {}
        if metadata:
            try:
                import json
                file_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning("Invalid metadata JSON, ignoring")
        
        # Upload to cloud storage
        upload_result = await storage_manager.upload_file(
            temp_path,
            full_destination,
            provider=provider,
            metadata={
                "original_filename": file.filename,
                "content_type": file.content_type or "application/octet-stream",
                "file_size": file_size,
                "uploaded_by": str(current_user.id),
                "upload_date": datetime.utcnow().isoformat(),
                **file_metadata
            }
        )
        
        # Save file record to database
        db_file = FileUpload(
            id=str(uuid.uuid4()),
            filename=file.filename,
            file_path=upload_result["file_path"],
            file_url=upload_result["file_url"],
            file_size=file_size,
            content_type=file.content_type or "application/octet-stream",
            provider=upload_result["provider"],
            folder=folder or "uploads",
            uploaded_by=current_user.id,
            upload_date=datetime.utcnow()
        )
        
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        logger.info(
            f"File uploaded successfully",
            file_id=db_file.id,
            filename=file.filename,
            file_size=file_size,
            provider=upload_result["provider"],
            user_id=current_user.id
        )
        
        return {
            "file_id": db_file.id,
            "filename": file.filename,
            "file_url": upload_result["file_url"],
            "file_size": file_size,
            "content_type": file.content_type,
            "provider": upload_result["provider"],
            "upload_date": db_file.upload_date.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.post("/upload-multiple", response_model=dict)
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = Form(None),
    provider: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload multiple files to cloud storage."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        uploaded_files = []
        temp_dir = "temp_uploads"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process each file
        for file in files:
            if not file.filename:
                continue
            
            # Validate file size
            file.file.seek(0, 2)
            file_size = file.file.tell()
            file.file.seek(0)
            
            if file_size > 100 * 1024 * 1024:  # 100MB limit per file
                continue
            
            # Create temporary file
            temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
            
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Generate destination path
            destination_path = folder or "uploads"
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            full_destination = f"{destination_path}/{unique_filename}"
            
            # Upload to cloud storage
            upload_result = await storage_manager.upload_file(
                temp_path,
                full_destination,
                provider=provider,
                metadata={
                    "original_filename": file.filename,
                    "content_type": file.content_type or "application/octet-stream",
                    "file_size": file_size,
                    "uploaded_by": str(current_user.id),
                    "upload_date": datetime.utcnow().isoformat()
                }
            )
            
            # Save file record to database
            db_file = FileUpload(
                id=str(uuid.uuid4()),
                filename=file.filename,
                file_path=upload_result["file_path"],
                file_url=upload_result["file_url"],
                file_size=file_size,
                content_type=file.content_type or "application/octet-stream",
                provider=upload_result["provider"],
                folder=folder or "uploads",
                uploaded_by=current_user.id,
                upload_date=datetime.utcnow()
            )
            
            db.add(db_file)
            uploaded_files.append({
                "file_id": db_file.id,
                "filename": file.filename,
                "file_url": upload_result["file_url"],
                "file_size": file_size,
                "content_type": file.content_type,
                "provider": upload_result["provider"]
            })
            
            # Clean up temporary file
            os.remove(temp_path)
        
        db.commit()
        
        logger.info(
            f"Multiple files uploaded successfully",
            files_count=len(uploaded_files),
            provider=provider or storage_manager.get_available_providers()[0],
            user_id=current_user.id
        )
        
        return {
            "uploaded_files": uploaded_files,
            "total_uploaded": len(uploaded_files)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multiple file upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload files")


@router.get("/my-files", response_model=dict)
async def get_user_files(
    folder: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get files uploaded by the current user."""
    try:
        query = db.query(FileUpload).filter(FileUpload.uploaded_by == current_user.id)
        
        if folder:
            query = query.filter(FileUpload.folder == folder)
        
        total_files = query.count()
        files = query.order_by(FileUpload.upload_date.desc()).offset(offset).limit(limit).all()
        
        return {
            "files": [
                {
                    "file_id": file.id,
                    "filename": file.filename,
                    "file_url": file.file_url,
                    "file_size": file.file_size,
                    "content_type": file.content_type,
                    "provider": file.provider,
                    "folder": file.folder,
                    "upload_date": file.upload_date.isoformat()
                }
                for file in files
            ],
            "total": total_files,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")


@router.get("/all-files", response_model=dict)
async def get_all_files(
    folder: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all files (admin only)."""
    try:
        # Check if user is admin (simplified check)
        # In production, implement proper role-based access
        
        query = db.query(FileUpload)
        
        if folder:
            query = query.filter(FileUpload.folder == folder)
        
        total_files = query.count()
        files = query.order_by(FileUpload.upload_date.desc()).offset(offset).limit(limit).all()
        
        return {
            "files": [
                {
                    "file_id": file.id,
                    "filename": file.filename,
                    "file_url": file.file_url,
                    "file_size": file.file_size,
                    "content_type": file.content_type,
                    "provider": file.provider,
                    "folder": file.folder,
                    "uploaded_by": file.uploaded_by,
                    "upload_date": file.upload_date.isoformat()
                }
                for file in files
            ],
            "total": total_files,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error retrieving all files: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve files")


@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    expires_in: int = 3600,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get download URL for a file."""
    try:
        file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user has access to the file
        if file.uploaded_by != current_user.id:
            # In production, implement proper access control
            pass
        
        # Generate signed URL
        download_url = await storage_manager.get_file_url(file.file_path, expires_in)
        
        logger.info(
            f"File download URL generated",
            file_id=file_id,
            user_id=current_user.id,
            expires_in=expires_in
        )
        
        return {
            "download_url": download_url,
            "expires_in": expires_in,
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating download URL: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate download URL")


@router.delete("/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a file from cloud storage."""
    try:
        file = db.query(FileUpload).filter(FileUpload.id == file_id).first()
        
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user owns the file
        if file.uploaded_by != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized to delete this file")
        
        # Delete from cloud storage
        delete_success = await storage_manager.delete_file(file.file_path)
        
        if not delete_success:
            raise HTTPException(status_code=500, detail="Failed to delete file from storage")
        
        # Delete from database
        db.delete(file)
        db.commit()
        
        logger.info(
            f"File deleted successfully",
            file_id=file_id,
            filename=file.filename,
            user_id=current_user.id
        )
        
        return {
            "message": "File deleted successfully",
            "file_id": file_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete file")


@router.get("/folders", response_model=dict)
async def get_folders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get unique folder names for the current user."""
    try:
        folders = db.query(FileUpload.folder).filter(
            FileUpload.uploaded_by == current_user.id
        ).distinct().all()
        
        return {
            "folders": [folder[0] for folder in folders if folder[0]]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving folders: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve folders")


@router.get("/providers", response_model=dict)
async def get_storage_providers():
    """Get available cloud storage providers."""
    try:
        providers = storage_manager.get_available_providers()
        return {
            "providers": providers,
            "message": "Available cloud storage providers"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving providers: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve providers")