#!/usr/bin/env python3
# Dolphin Control - Interface for local LLM to control your computer
# Provides a secure way to allow your local LLM to execute system commands

import argparse
import json
import logging
import os
import platform
import re
import subprocess
import sys
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Union

# Set up basic logging first (will be replaced with rich logging if available)
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
log = logging.getLogger("dolphin_control")

# Try importing dependencies with proper error messages
try:
    import requests
except ImportError:
    log.error("Required package 'requests' not found. Install with: pip install requests")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.logging import RichHandler
    from rich.prompt import Confirm, Prompt
    
    # Replace basic logging with rich logging
    console = Console()
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
        force=True
    )
    log = logging.getLogger("dolphin_control")
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None
    log.error("Package 'rich' not found. Install with: pip install rich")
    sys.exit(1)

# Optional imports with graceful fallbacks
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    log.warning("Package 'psutil' not found. System info commands will be limited.")

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    log.warning("Package 'pyautogui' not found. Screenshot functionality will be disabled.")

class CommandCategory(Enum):
    FILE_SYSTEM = "file_system"
    PROCESS = "process"
    NETWORK = "network"
    SYSTEM_INFO = "system_info"
    APPLICATION = "application"
    SCREEN = "screen"  # New category
    CUSTOM = "custom"

class DolphinControl:
    def __init__(self, ollama_url: str = "http://localhost:11434", 
                 model_name: str = "dolphin",
                 history_file: str = "dolphin_history.json",
                 safe_mode: bool = True,
                 auto_confirm: bool = False,
                 enable_screen_watching: bool = False):
        self.ollama_url = ollama_url
        self.model_name = model_name
        self.history_file = Path(history_file)
        self.safe_mode = safe_mode
        self.auto_confirm = auto_confirm
        self.history = []
        self.commands = {}
        self.last_response = ""
        
        # Initialize screen watcher if enabled
        self.screen_watcher = None
        if enable_screen_watching:
            try:
                from screen_watcher import ScreenWatcher
                self.screen_watcher = ScreenWatcher()
                log.info("Screen watching enabled")
            except ImportError:
                log.warning("Could not import screen_watcher module. Screen watching will be disabled.")
        
        # Check if Ollama is running
        self._check_ollama_connection()
        
        # Load history if exists
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                log.info(f"Loaded conversation history from {self.history_file}")
            except json.JSONDecodeError:
                log.warning(f"Could not parse history file {self.history_file}. Starting with empty history.")
            except Exception as e:
                log.warning(f"Error loading history: {str(e)}. Starting with empty history.")
        
        # Register commands
        self._register_commands()

    def _register_commands(self):
        """Register all available commands"""
        # Existing commands...
        
        # Screen watching commands
        if self.screen_watcher:
            self.register_command("start_watching", self.start_screen_watching,
                                "Start watching the screen", CommandCategory.SCREEN)
            self.register_command("stop_watching", self.stop_screen_watching,
                                "Stop watching the screen", CommandCategory.SCREEN)
            self.register_command("get_screen_info", self.get_screen_info,
                                "Get current screen information", CommandCategory.SCREEN)
    
    def start_screen_watching(self) -> Dict:
        """Start watching the screen"""
        if not self.screen_watcher:
            return {"success": False, "error": "Screen watching is not enabled"}
        
        try:
            self.screen_watcher.start_watching()
            return {
                "success": True,
                "message": "Started watching screen"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def stop_screen_watching(self) -> Dict:
        """Stop watching the screen"""
        if not self.screen_watcher:
            return {"success": False, "error": "Screen watching is not enabled"}
        
        try:
            self.screen_watcher.stop_watching()
            return {
                "success": True,
                "message": "Stopped watching screen"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_screen_info(self) -> Dict:
        """Get current screen information"""
        if not self.screen_watcher:
            return {"success": False, "error": "Screen watching is not enabled"}
        
        try:
            analysis = self.screen_watcher.analyze_screen()
            return {
                "success": True,
                "screen_info": analysis
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def query_dolphin(self, user_input: str) -> str:
        """Query the Dolphin model"""
        try:
            # Add screen information to the context if available
            context = ""
            if self.screen_watcher:
                try:
                    analysis = self.screen_watcher.analyze_screen()
                    context = f"\nScreen Context:\nText: {analysis['text']}\n"
                    if analysis['ui_elements']:
                        context += "UI Elements:\n"
                        for elem in analysis['ui_elements']:
                            if elem['text']:
                                context += f"- {elem['text']} at position {elem['bounds']}\n"
                except Exception as e:
                    log.warning(f"Error getting screen context: {str(e)}")
            
            # Prepare the messages history
            messages = [{"role": "system", "content": 
                        f"""You are Dolphin, a helpful AI assistant that can control a computer by executing commands.
                        You can run commands to get information and perform tasks on the user's computer.
                        When you need to execute a command, respond in this exact format:
                        
                        <execute>
                        {{
                            "command": "command_name",
                            "params": {{
                                "param1": "value1",
                                "param2": "value2"
                            }}
                        }}
                        </execute>
                        
                        Available commands:
                        {chr(10).join([f"- {cmd.name}: {cmd.description}" for cmd in self.commands.values()])}
                        
                        {context}"""}]
            
            # Add the conversation history
            for entry in self.history:
                messages.append(entry)
            
            # Add the user's input
            messages.append({"role": "user", "content": user_input})
            
            # Make the API request
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=90
            )
            
            if response.status_code == 200:
                result = response.json()
                self.last_response = result["message"]["content"]
                return self.last_response
            else:
                log.error(f"Error from Ollama API: {response.status_code} - {response.text}")
                return f"Error: {response.status_code} - {response.text}"
        except requests.exceptions.Timeout:
            error_msg = "Request to Ollama timed out. The model might be processing a complex query."
            log.error(error_msg)
            return error_msg
        except requests.exceptions.ConnectionError:
            error_msg = f"Connection error when contacting Ollama at {self.ollama_url}. Is the server still running?"
            log.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Error querying Dolphin: {str(e)}"
            log.error(error_msg)
            return error_msg 