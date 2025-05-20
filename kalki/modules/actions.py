import pyautogui
import subprocess
import webbrowser
import logging
from typing import Optional, Dict, Any, Tuple
import time

logger = logging.getLogger(__name__)

class ActionEngine:
    def __init__(self, safe_mode: bool = True):
        """Initialize the action engine with safety controls"""
        self.safe_mode = safe_mode
        pyautogui.FAILSAFE = True
        self._setup_pyautogui()
        
    def _setup_pyautogui(self):
        """Configure PyAutoGUI settings"""
        pyautogui.PAUSE = 0.5  # Add small delay between actions
        
    def click(self, x: int, y: int, button: str = 'left'):
        """Click at specific coordinates"""
        try:
            pyautogui.click(x=x, y=y, button=button)
            logger.info(f"Clicked at coordinates ({x}, {y})")
        except Exception as e:
            logger.error(f"Click failed: {e}")
            raise
            
    def click_text(self, text: str, confidence: float = 0.7) -> bool:
        """Find and click text on screen"""
        try:
            location = pyautogui.locateOnScreen(text, confidence=confidence)
            if location:
                center = pyautogui.center(location)
                self.click(center.x, center.y)
                return True
            return False
        except Exception as e:
            logger.error(f"Text click failed: {e}")
            return False
            
    def type_text(self, text: str, interval: float = 0.1):
        """Type text with optional delay between characters"""
        try:
            pyautogui.write(text, interval=interval)
            logger.info(f"Typed text: {text}")
        except Exception as e:
            logger.error(f"Typing failed: {e}")
            raise
            
    def press_key(self, key: str):
        """Press a single key"""
        try:
            pyautogui.press(key)
            logger.info(f"Pressed key: {key}")
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            raise
            
    def hotkey(self, *keys):
        """Press a combination of keys"""
        try:
            pyautogui.hotkey(*keys)
            logger.info(f"Pressed hotkey: {' + '.join(keys)}")
        except Exception as e:
            logger.error(f"Hotkey failed: {e}")
            raise
            
    def open_application(self, app_name: str) -> bool:
        """Open an application by name"""
        try:
            subprocess.Popen([app_name])
            logger.info(f"Opened application: {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to open application: {e}")
            return False
            
    def open_url(self, url: str):
        """Open URL in default browser"""
        try:
            webbrowser.open(url)
            logger.info(f"Opened URL: {url}")
        except Exception as e:
            logger.error(f"Failed to open URL: {e}")
            raise
            
    def wait_for_text(self, text: str, timeout: int = 10, confidence: float = 0.7) -> bool:
        """Wait for text to appear on screen"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if pyautogui.locateOnScreen(text, confidence=confidence):
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
        
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse coordinates"""
        x, y = pyautogui.position()
        return (x, y)
        
    def move_mouse(self, x: int, y: int, duration: float = 0.2):
        """Move mouse to coordinates"""
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"Moved mouse to ({x}, {y})")
        except Exception as e:
            logger.error(f"Mouse movement failed: {e}")
            raise 