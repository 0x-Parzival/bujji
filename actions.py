import os
import subprocess
import logging
from typing import Optional
import webbrowser
import pyautogui
from urllib.parse import urlparse

class ActionEngine:
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.logger = logging.getLogger("kalki.actions")
        
        # Initialize PyAutoGUI safely
        pyautogui.FAILSAFE = True
        
    def is_safe_url(self, url: str) -> bool:
        """Check if URL is safe to open"""
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
        
    def open_url(self, url: str) -> bool:
        """Safely open URL in default browser"""
        if not self.is_safe_url(url):
            self.logger.warning(f"Unsafe URL detected: {url}")
            return False
            
        try:
            webbrowser.open(url)
            return True
        except Exception as e:
            self.logger.error(f"Error opening URL: {str(e)}")
            return False
            
    def run_command(self, command: str) -> Optional[str]:
        """Run system command with safety checks"""
        if self.safe_mode:
            # List of dangerous commands to block
            dangerous = ['rm', 'del', 'format', 'mkfs', ':(){:|:&}']
            if any(cmd in command.lower() for cmd in dangerous):
                self.logger.warning(f"Dangerous command blocked: {command}")
                return None
                
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout
        except Exception as e:
            self.logger.error(f"Error running command: {str(e)}")
            return None
            
    def click_element(self, target: str, confidence: float = 0.9) -> bool:
        """Click UI element by image matching"""
        try:
            location = pyautogui.locateOnScreen(target, confidence=confidence)
            if location:
                pyautogui.click(location)
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error clicking element: {str(e)}")
            return False
            
    def type_text(self, text: str, interval: float = 0.1) -> None:
        """Type text with natural delay"""
        try:
            pyautogui.write(text, interval=interval)
        except Exception as e:
            self.logger.error(f"Error typing text: {str(e)}")
            
    def press_key(self, key: str) -> None:
        """Press a keyboard key"""
        try:
            pyautogui.press(key)
        except Exception as e:
            self.logger.error(f"Error pressing key: {str(e)}")
            
    def move_mouse(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=0.2)
        except Exception as e:
            self.logger.error(f"Error moving mouse: {str(e)}")
            
    def take_screenshot(self, region: Optional[tuple] = None) -> Optional[str]:
        """Take screenshot of full screen or region"""
        try:
            if region:
                return pyautogui.screenshot(region=region)
            return pyautogui.screenshot()
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {str(e)}")
            return None 