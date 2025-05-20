import mss
import numpy as np
import pytesseract
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

class VisionSystem:
    def __init__(self):
        self.screen = mss.mss()
        self._setup_tesseract()
        
    def _setup_tesseract(self):
        """Configure Tesseract settings"""
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error(f"Tesseract not properly installed: {e}")
            raise RuntimeError("Tesseract OCR is required but not found")
    
    def capture_screen(self, monitor: int = 1) -> np.ndarray:
        """Capture screen content from specified monitor"""
        try:
            screenshot = self.screen.grab(self.screen.monitors[monitor])
            return np.array(screenshot)
        except Exception as e:
            logger.error(f"Failed to capture screen: {e}")
            raise
    
    def capture_active_window(self) -> np.ndarray:
        """Capture currently active window"""
        # TODO: Implement active window detection
        return self.capture_screen()
    
    def find_text_on_screen(self, text: str, confidence: float = 0.6) -> List[Dict[str, int]]:
        """Find all occurrences of text on screen with their bounding boxes"""
        screen = self.capture_screen()
        return self.find_text_in_image(screen, text, confidence)
    
    def find_text_in_image(self, image: np.ndarray, text: str, confidence: float = 0.6) -> List[Dict[str, int]]:
        """Find text in image and return bounding boxes"""
        try:
            # Convert to PIL Image if needed
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Get OCR data with bounding boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Find matches
            boxes = []
            for i, word in enumerate(data['text']):
                if text.lower() in word.lower():
                    if float(data['conf'][i]) >= confidence * 100:
                        boxes.append({
                            'x': data['left'][i],
                            'y': data['top'][i],
                            'width': data['width'][i],
                            'height': data['height'][i],
                            'confidence': float(data['conf'][i]) / 100
                        })
            
            return boxes
            
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return []
    
    def get_all_text_on_screen(self) -> str:
        """Get all visible text from screen"""
        screen = self.capture_screen()
        return self.get_text_from_image(screen)
    
    def get_text_from_image(self, image: np.ndarray) -> str:
        """Extract all text from image"""
        try:
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            return pytesseract.image_to_string(image)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return ""
            
    def close(self):
        """Clean up resources"""
        self.screen.close() 