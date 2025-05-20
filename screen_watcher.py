#!/usr/bin/env python3

import cv2
import mss
import numpy as np
import pytesseract
from PIL import Image
import time
import logging
from typing import Dict, List, Optional, Tuple

log = logging.getLogger("screen_watcher")

class ScreenWatcher:
    def __init__(self, capture_interval: float = 1.0):
        """Initialize the screen watcher.
        
        Args:
            capture_interval: Time between screen captures in seconds
        """
        self.capture_interval = capture_interval
        self.sct = mss.mss()
        self.last_capture = None
        self.last_text = ""
        self.running = False
        
        # Configure Tesseract
        self.tesseract_config = r'--oem 3 --psm 6'
    
    def capture_screen(self) -> np.ndarray:
        """Capture the current screen content."""
        monitor = self.sct.monitors[0]  # Primary monitor
        screenshot = self.sct.grab(monitor)
        
        # Convert to numpy array
        img = np.array(screenshot)
        
        # Convert from BGRA to BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        self.last_capture = img
        return img
    
    def extract_text(self, img: np.ndarray) -> str:
        """Extract text from the image using OCR."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get black and white image
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # OCR
            text = pytesseract.image_to_string(thresh, config=self.tesseract_config)
            self.last_text = text
            return text
        except Exception as e:
            log.error(f"Error extracting text: {str(e)}")
            return ""
    
    def detect_ui_elements(self, img: np.ndarray) -> List[Dict]:
        """Detect UI elements in the image."""
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            ui_elements = []
            for contour in contours:
                # Get bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter out very small elements
                if w < 20 or h < 20:
                    continue
                
                # Extract the region
                roi = img[y:y+h, x:x+w]
                
                # Get text in this region
                text = self.extract_text(roi)
                
                ui_elements.append({
                    'type': 'unknown',
                    'bounds': (x, y, w, h),
                    'text': text.strip()
                })
            
            return ui_elements
        except Exception as e:
            log.error(f"Error detecting UI elements: {str(e)}")
            return []
    
    def analyze_screen(self) -> Dict:
        """Capture and analyze the current screen content."""
        img = self.capture_screen()
        text = self.extract_text(img)
        ui_elements = self.detect_ui_elements(img)
        
        return {
            'text': text,
            'ui_elements': ui_elements,
            'timestamp': time.time()
        }
    
    def start_watching(self):
        """Start continuous screen watching."""
        self.running = True
        while self.running:
            try:
                analysis = self.analyze_screen()
                log.info(f"Found {len(analysis['ui_elements'])} UI elements")
                time.sleep(self.capture_interval)
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                log.error(f"Error in screen watching: {str(e)}")
                time.sleep(1)  # Wait before retrying
    
    def stop_watching(self):
        """Stop screen watching."""
        self.running = False 