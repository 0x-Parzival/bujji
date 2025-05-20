#!/usr/bin/env python3

import logging
import os
import platform
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Union

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

log = logging.getLogger("action_engine")

class ActionEngine:
    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self._init_tts()
        
        if PYAUTOGUI_AVAILABLE:
            # Configure PyAutoGUI
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        self.tts_engine = None
        if TTS_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                log.info("Text-to-speech initialized")
            except Exception as e:
                log.warning(f"Failed to initialize text-to-speech: {str(e)}")
    
    def execute_command(self, command: str, args: List[str] = None) -> Dict:
        """Execute a system command"""
        if args is None:
            args = []
        
        if self.safe_mode:
            # Check for potentially dangerous commands
            dangerous_patterns = [
                "rm -rf", "format", "mkfs", "dd if=", ":(){:|:}",
                ">/dev/sd", "chmod -R", "chown -R", "wget.*|.*sh",
                "curl.*|.*sh", "^sudo", "^su\\s"
            ]
            
            for pattern in dangerous_patterns:
                if pattern in command:
                    return {
                        "success": False,
                        "error": f"Potentially dangerous command detected: {command}"
                    }
        
        try:
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "success": True,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def open_url(self, url: str) -> Dict:
        """Open a URL in the default browser"""
        try:
            webbrowser.open(url)
            return {"success": True, "message": f"Opened URL: {url}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_click(self, x: int, y: int) -> Dict:
        """Click at specific coordinates"""
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "PyAutoGUI not available"}
        
        try:
            pyautogui.click(x, y)
            return {"success": True, "message": f"Clicked at ({x}, {y})"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def type_text(self, text: str) -> Dict:
        """Type text using keyboard"""
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "PyAutoGUI not available"}
        
        try:
            pyautogui.write(text)
            return {"success": True, "message": f"Typed text: {text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def press_key(self, key: str) -> Dict:
        """Press a keyboard key"""
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "PyAutoGUI not available"}
        
        try:
            pyautogui.press(key)
            return {"success": True, "message": f"Pressed key: {key}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def speak_text(self, text: str) -> Dict:
        """Speak text using TTS"""
        if not self.tts_engine:
            return {"success": False, "error": "Text-to-speech not available"}
        
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            return {"success": True, "message": "Spoke text successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def find_on_screen(self, image_path: Union[str, Path]) -> Dict:
        """Find an image on screen and return its position"""
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "PyAutoGUI not available"}
        
        try:
            location = pyautogui.locateOnScreen(str(image_path), confidence=0.9)
            if location:
                return {
                    "success": True,
                    "location": location,
                    "center": pyautogui.center(location)
                }
            else:
                return {"success": False, "error": "Image not found on screen"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def click_element(self, element_info: Dict) -> Dict:
        """Click a UI element based on its information"""
        if not PYAUTOGUI_AVAILABLE:
            return {"success": False, "error": "PyAutoGUI not available"}
        
        try:
            x, y, w, h = element_info["bounds"]
            center_x = x + w // 2
            center_y = y + h // 2
            
            return self.mouse_click(center_x, center_y)
        except Exception as e:
            return {"success": False, "error": str(e)} 