import pytesseract
import easyocr
import cv2
import numpy as np
from PIL import Image
import io
import logging
from typing import Dict, List, Optional, Tuple
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class OCRResult:
    text: str
    confidence: float
    bounding_boxes: List[Dict]
    extracted_data: Dict

class OCRService:
    def __init__(self):
        """Initialize OCR service with both Tesseract and EasyOCR"""
        self.easyocr_reader = easyocr.Reader(['en'])
        
    async def process_document(self, image_data: bytes, document_type: str = "general") -> OCRResult:
        """
        Process document with OCR and extract structured data
        
        Args:
            image_data: Raw image bytes
            document_type: Type of document (invoice, receipt, contract, etc.)
            
        Returns:
            OCRResult with extracted text and structured data
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image
            processed_image = self._preprocess_image(image)
            
            # Perform OCR with both engines
            tesseract_result = self._tesseract_ocr(processed_image)
            easyocr_result = self._easyocr_ocr(processed_image)
            
            # Combine results and choose best
            combined_text, confidence, bounding_boxes = self._combine_ocr_results(
                tesseract_result, easyocr_result
            )
            
            # Extract structured data based on document type
            extracted_data = await self._extract_structured_data(
                combined_text, document_type
            )
            
            return OCRResult(
                text=combined_text,
                confidence=confidence,
                bounding_boxes=bounding_boxes,
                extracted_data=extracted_data
            )
            
        except Exception as e:
            logger.error(f"OCR processing failed: {str(e)}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def _preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert PIL to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # Deskew if needed
        deskewed = self._deskew_image(thresh)
        
        return deskewed
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Correct skew in the image"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
            
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
            
        # Only correct if angle is significant
        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
            return rotated
        
        return image
    
    def _tesseract_ocr(self, image: np.ndarray) -> Tuple[str, float, List[Dict]]:
        """Perform OCR using Tesseract"""
        try:
            # Get detailed data from Tesseract
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Extract text and confidence
            text_parts = []
            confidences = []
            bounding_boxes = []
            
            for i in range(len(data['text'])):
                if int(data['conf'][i]) > 30:  # Filter low confidence
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(data['conf'][i]))
                        bounding_boxes.append({
                            'text': text,
                            'x': int(data['left'][i]),
                            'y': int(data['top'][i]),
                            'width': int(data['width'][i]),
                            'height': int(data['height'][i]),
                            'confidence': int(data['conf'][i])
                        })
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return full_text, avg_confidence, bounding_boxes
            
        except Exception as e:
            logger.error(f"Tesseract OCR failed: {str(e)}")
            return "", 0, []
    
    def _easyocr_ocr(self, image: np.ndarray) -> Tuple[str, float, List[Dict]]:
        """Perform OCR using EasyOCR"""
        try:
            results = self.easyocr_reader.readtext(image)
            
            text_parts = []
            confidences = []
            bounding_boxes = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filter low confidence
                    text_parts.append(text)
                    confidences.append(confidence * 100)  # Convert to percentage
                    
                    # Convert bbox to standard format
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    bounding_boxes.append({
                        'text': text,
                        'x': int(min(x_coords)),
                        'y': int(min(y_coords)),
                        'width': int(max(x_coords) - min(x_coords)),
                        'height': int(max(y_coords) - min(y_coords)),
                        'confidence': confidence * 100
                    })
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return full_text, avg_confidence, bounding_boxes
            
        except Exception as e:
            logger.error(f"EasyOCR failed: {str(e)}")
            return "", 0, []
    
    def _combine_ocr_results(self, tesseract_result: Tuple, easyocr_result: Tuple) -> Tuple[str, float, List[Dict]]:
        """Combine results from both OCR engines"""
        tesseract_text, tesseract_conf, tesseract_boxes = tesseract_result
        easyocr_text, easyocr_conf, easyocr_boxes = easyocr_result
        
        # Choose the result with higher confidence
        if tesseract_conf > easyocr_conf:
            return tesseract_text, tesseract_conf, tesseract_boxes
        else:
            return easyocr_text, easyocr_conf, easyocr_boxes
    
    async def _extract_structured_data(self, text: str, document_type: str) -> Dict:
        """Extract structured data based on document type"""
        extracted_data = {}
        
        if document_type == "invoice":
            extracted_data = self._extract_invoice_data(text)
        elif document_type == "receipt":
            extracted_data = self._extract_receipt_data(text)
        elif document_type == "contract":
            extracted_data = self._extract_contract_data(text)
        else:
            extracted_data = self._extract_general_data(text)
        
        return extracted_data
    
    def _extract_invoice_data(self, text: str) -> Dict:
        """Extract invoice-specific data"""
        data = {}
        
        # Extract invoice number
        invoice_patterns = [
            r'invoice\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'inv\s*#?\s*:?\s*([A-Z0-9\-]+)',
            r'#\s*([A-Z0-9\-]+)'
        ]
        
        for pattern in invoice_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['invoice_number'] = match.group(1)
                break
        
        # Extract dates
        date_patterns = [
            r'date\s*:?\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        if dates:
            data['date'] = dates[0]
        
        # Extract amounts
        amount_patterns = [
            r'total\s*:?\s*\$?(\d+[,.]?\d*\.?\d{2})',
            r'amount\s*:?\s*\$?(\d+[,.]?\d*\.?\d{2})',
            r'\$(\d+[,.]?\d*\.?\d{2})'
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        
        if amounts:
            # Convert to float and find the largest (likely total)
            numeric_amounts = []
            for amount in amounts:
                try:
                    clean_amount = amount.replace(',', '')
                    numeric_amounts.append(float(clean_amount))
                except ValueError:
                    continue
            
            if numeric_amounts:
                data['total_amount'] = max(numeric_amounts)
        
        # Extract vendor/company name (usually at the top)
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d', line):
                data['vendor'] = line
                break
        
        return data
    
    def _extract_receipt_data(self, text: str) -> Dict:
        """Extract receipt-specific data"""
        # Similar to invoice but simpler
        return self._extract_invoice_data(text)
    
    def _extract_contract_data(self, text: str) -> Dict:
        """Extract contract-specific data"""
        data = {}
        
        # Extract parties
        party_patterns = [
            r'between\s+([^,\n]+)\s+and\s+([^,\n]+)',
            r'party\s+of\s+the\s+first\s+part[:\s]+([^,\n]+)',
            r'party\s+of\s+the\s+second\s+part[:\s]+([^,\n]+)'
        ]
        
        for pattern in party_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if 'between' in pattern:
                    data['party_1'] = match.group(1).strip()
                    data['party_2'] = match.group(2).strip()
                else:
                    if 'first' in pattern:
                        data['party_1'] = match.group(1).strip()
                    else:
                        data['party_2'] = match.group(1).strip()
        
        # Extract contract type
        contract_patterns = [
            r'(employment|service|lease|purchase|sales?)\s+agreement',
            r'(employment|service|lease|purchase|sales?)\s+contract'
        ]
        
        for pattern in contract_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data['contract_type'] = match.group(1).lower()
                break
        
        return data
    
    def _extract_general_data(self, text: str) -> Dict:
        """Extract general data from any document"""
        data = {}
        
        # Extract emails
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            data['emails'] = emails
        
        # Extract phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            data['phone_numbers'] = [''.join(phone) for phone in phones]
        
        # Extract dates
        date_pattern = r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        if dates:
            data['dates'] = dates
        
        # Extract amounts
        amount_pattern = r'\$\d+[,.]?\d*\.?\d{2}'
        amounts = re.findall(amount_pattern, text)
        if amounts:
            data['amounts'] = amounts
        
        return data