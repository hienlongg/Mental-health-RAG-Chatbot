"""Document management endpoints."""
from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
import os
import shutil

documents_router = APIRouter(prefix="/documents", tags=["documents"])

# Configuration for file uploads
UPLOAD_FOLDER = Path('./data/documents')
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'docx', 'doc'}

# Create upload folder if it doesn't exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_router.get("/list")
async def list_documents():
    """List all uploaded documents.
    
    Returns:
        JSON response with list of documents
    """
    try:
        documents = []
        if UPLOAD_FOLDER.exists():
            documents = [f.name for f in UPLOAD_FOLDER.iterdir() if f.is_file()]
        
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


@documents_router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload a new document.
    
    Args:
        file: The document file to upload
    
    Returns:
        JSON response with upload status
    """
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file selected")
        
        if not allowed_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        filepath = UPLOAD_FOLDER / file.filename
        
        # Save file
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "success": True,
            "message": "Document uploaded successfully",
            "filename": file.filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@documents_router.delete("/{filename}")
async def delete_document(filename: str):
    """Delete a document.
    
    Args:
        filename: The name of the file to delete
    
    Returns:
        JSON response with deletion status
    """
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        filepath.unlink()
        
        return {
            "success": True,
            "message": "Document deleted successfully",
            "filename": filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@documents_router.get("/{filename}")
async def get_document(filename: str):
    """Get information about a specific document.
    
    Args:
        filename: The name of the file
    
    Returns:
        JSON response with document information
    """
    try:
        filepath = UPLOAD_FOLDER / filename
        
        if not filepath.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        
        file_stats = filepath.stat()
        
        return {
            "success": True,
            "filename": filename,
            "size": file_stats.st_size,
            "created": file_stats.st_ctime,
            "modified": file_stats.st_mtime
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
