from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Optional
import logging

from ..services.ocr_service import OCRService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OCR service
ocr_service = OCRService()

@router.post("/process")
async def process_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = "general"
):
    """
    Process uploaded document with OCR and extract structured data
    """
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/gif", "application/pdf"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process with OCR
        result = await ocr_service.process_document(file_content, document_type)
        
        return {
            "success": True,
            "filename": file.filename,
            "document_type": document_type,
            "ocr_result": {
                "text": result.text,
                "confidence": result.confidence,
                "extracted_data": result.extracted_data,
                "bounding_boxes_count": len(result.bounding_boxes)
            }
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported-types")
async def get_supported_types():
    """
    Get list of supported document types for processing
    """
    return {
        "supported_types": [
            {
                "type": "invoice",
                "description": "Business invoices with vendor, amounts, and dates",
                "credits_required": 5
            },
            {
                "type": "receipt",
                "description": "Purchase receipts and transaction records",
                "credits_required": 3
            },
            {
                "type": "contract",
                "description": "Legal contracts and agreements",
                "credits_required": 8
            },
            {
                "type": "general",
                "description": "General document text extraction",
                "credits_required": 2
            }
        ]
    }