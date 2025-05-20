#!/usr/bin/env python3

import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
import base64

log = logging.getLogger("model_handler")

class BaseModelHandler(ABC):
    def __init__(self, model_url: str = "http://localhost:11434"):
        self.model_url = model_url
        self._check_connection()
    
    def _check_connection(self) -> None:
        """Check if the model server is running"""
        try:
            response = requests.get(f"{self.model_url}/api/version", timeout=5)
            if response.status_code == 200:
                version_info = response.json()
                log.info(f"Connected to model server version {version_info.get('version', 'unknown')}")
            else:
                raise ConnectionError(f"Model server returned status code {response.status_code}")
        except Exception as e:
            raise ConnectionError(f"Cannot connect to model server at {self.model_url}: {str(e)}")
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate a response from the model"""
        pass

class DolphinHandler(BaseModelHandler):
    def __init__(self, model_url: str = "http://localhost:11434", model_name: str = "dolphin-mixtral"):
        super().__init__(model_url)
        self.model_name = model_name
    
    def generate(self, prompt: str, context: str = "", history: List[Dict] = None) -> str:
        """Generate a response using the Dolphin model"""
        try:
            messages = []
            if history:
                messages.extend(history)
            
            messages.append({"role": "user", "content": prompt})
            
            response = requests.post(
                f"{self.model_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": messages,
                    "stream": False
                },
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()["message"]["content"]
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

class QwenHandler(BaseModelHandler):
    def __init__(self, model_url: str = "http://localhost:11434", model_name: str = "qwen:2.5vl"):
        super().__init__(model_url)
        self.model_name = model_name
    
    def generate(self, prompt: str, image_path: Optional[Path] = None) -> str:
        """Generate a response using the Qwen model"""
        try:
            data = {
                "model": self.model_name,
                "prompt": prompt
            }
            
            # Add image data if provided
            if image_path:
                if not image_path.exists():
                    raise FileNotFoundError(f"Image not found: {image_path}")
                with open(image_path, "rb") as f:
                    data["images"] = [f.read()]
            
            response = requests.post(
                f"{self.model_url}/api/generate",
                json=data,
                timeout=90
            )
            
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

class ModelRouter:
    def __init__(self, model_url: str = "http://localhost:11434"):
        self.model_url = model_url
        self.dolphin = DolphinHandler(model_url)
        self.qwen = QwenHandler(model_url)
    
    def route_task(self, prompt: str, image_path: Optional[Path] = None, 
                  context: str = "", history: List[Dict] = None) -> str:
        """Route the task to the appropriate model"""
        try:
            # If image is provided, use Qwen
            if image_path:
                return self.qwen.generate(prompt, image_path)
            
            # Otherwise use Dolphin
            return self.dolphin.generate(prompt, context, history)
        except Exception as e:
            raise Exception(f"Error routing task: {str(e)}")

class ModelHandler:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.logger = logging.getLogger("kalki.model")
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def generate(self, 
                prompt: str, 
                model: str = "dolphin3", 
                system: Optional[str] = None,
                image_path: Optional[str] = None,
                **kwargs) -> Dict[Any, Any]:
        """
        Generate a response using Ollama API
        
        Args:
            prompt: The text prompt to send
            model: Model name (default: dolphin3)
            system: Optional system prompt
            image_path: Optional path to image for visual tasks
            **kwargs: Additional parameters to pass to Ollama API
        """
        # For qwen with image input, use the generate API
        if image_path and "qwen" in model:
            url = f"{self.base_url}/api/generate"
            
            # Read and encode image
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            data = {
                "model": model,
                "prompt": prompt,
                "images": [image_data],
                **kwargs
            }
            
            if system:
                data["system"] = system
                
            try:
                response = requests.post(url, json=data, headers=self.headers)
                response.raise_for_status()
                return {
                    "text": response.json()["response"]
                }
            except Exception as e:
                self.logger.error(f"Error calling Ollama API: {str(e)}")
                raise
        
        # For text-only tasks, use the chat API
        else:
            url = f"{self.base_url}/api/chat"
            
            messages = [{"role": "user", "content": prompt}]
            if system:
                messages.insert(0, {"role": "system", "content": system})

            data = {
                "model": model,
                "messages": messages,
                "stream": False,
                **kwargs
            }

            try:
                response = requests.post(url, json=data, headers=self.headers)
                response.raise_for_status()
                return {
                    "text": response.json()["message"]["content"]
                }
                
            except Exception as e:
                self.logger.error(f"Error calling Ollama API: {str(e)}")
                raise

    def list_models(self) -> list:
        """Get list of available models from Ollama"""
        url = f"{self.base_url}/api/tags"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return [model["name"] for model in response.json()["models"]]
        except Exception as e:
            self.logger.error(f"Error getting models: {str(e)}")
            raise 