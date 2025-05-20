import requests
from requests.adapters import HTTPAdapter, Retry
from typing import Optional, Dict, Any, List
import logging
import asyncio
import aiohttp
import json

class JanClient:
    def __init__(self, 
                 base_url: str = "http://localhost:8080", 
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logging.getLogger("kalki.jan")
        
        # Default model configuration
        self.default_model = "phi-4-reasoning:4b"
        self.model_configs = {
            "phi-4-reasoning:4b": {
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 2048,
                "presence_penalty": 0.0,
                "frequency_penalty": 0.0,
                "stop": None
            }
        }
        
        # Set up headers
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
        # Set up session with retry logic
        self.session = requests.Session()
        retries = Retry(total=max_retries,
                       backoff_factor=0.5,
                       status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        
    async def agenerate(self,
                       prompt: str,
                       model: str = "dolphin",
                       image_path: Optional[str] = None,
                       **kwargs) -> Dict[Any, Any]:
        """
        Async version of generate method
        """
        url = f"{self.base_url}/v1/chat/completions"
        messages = [{"role": "user", "content": prompt}]
        data = {
            "messages": messages,
            "model": model,
            **kwargs
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                if image_path:
                    with open(image_path, "rb") as f:
                        data = aiohttp.FormData()
                        data.add_field("image", f)
                        data.add_field("messages", json.dumps(messages))
                        async with session.post(url, data=data, headers=self.headers) as response:
                            response.raise_for_status()
                            result = await response.json()
                else:
                    async with session.post(url, json=data, headers=self.headers) as response:
                        response.raise_for_status()
                        result = await response.json()
                
                return {
                    "text": result["choices"][0]["message"]["content"],
                    "model": model,
                    "usage": result.get("usage", {})
                }
            
            except Exception as e:
                self.logger.error(f"Error in async call to Jan API: {str(e)}")
                raise

    def generate(self,
                prompt: str,
                model: str = "dolphin",
                image_path: Optional[str] = None,
                **kwargs) -> Dict[Any, Any]:
        """
        Generate a response from Jan using specified model
        
        Args:
            prompt: The text prompt to send
            model: Model name to use (e.g. "dolphin", "qwen2.5:0.5b")
            image_path: Optional path to image for multimodal models
            **kwargs: Additional parameters to pass to Jan API
        """
        url = f"{self.base_url}/v1/chat/completions"
        messages = [{"role": "user", "content": prompt}]
        data = {
            "messages": messages,
            "model": model,
            **kwargs
        }

        try:
            if image_path:
                with open(image_path, "rb") as f:
                    files = {"image": f}
                    response = self.session.post(
                        url,
                        data=data,
                        files=files,
                        headers=self.headers,
                        timeout=self.timeout
                    )
            else:
                response = self.session.post(
                    url,
                    json=data,
                    headers=self.headers,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            result = response.json()
            return {
                "text": result["choices"][0]["message"]["content"],
                "model": model,
                "usage": result.get("usage", {})
            }
            
        except requests.exceptions.Timeout:
            self.logger.error("Request timed out")
            raise
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error calling Jan API: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            raise

    def list_models(self) -> List[str]:
        """Get list of available models from Jan"""
        url = f"{self.base_url}/v1/models"
        try:
            response = self.session.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return [model["id"] for model in response.json()["data"]]
        except Exception as e:
            self.logger.error(f"Error getting models: {str(e)}")
            raise

    def check_health(self) -> bool:
        """Check if Jan.ai server is healthy"""
        try:
            response = self.session.get(
                f"{self.base_url}/v1/models",
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

    def generate_with_phi(self,
                         prompt: str,
                         temperature: Optional[float] = None,
                         max_tokens: Optional[int] = None) -> Dict[Any, Any]:
        """
        Generate a response using Phi-4-Reasoning model with optimized parameters
        
        Args:
            prompt: The text prompt to send
            temperature: Optional override for temperature (default: 0.7)
            max_tokens: Optional override for max_tokens (default: 2048)
        """
        config = self.model_configs["phi-4-reasoning:4b"].copy()
        if temperature is not None:
            config["temperature"] = temperature
        if max_tokens is not None:
            config["max_tokens"] = max_tokens
            
        return self.generate(prompt, model="phi-4-reasoning:4b", **config)
            
    def __del__(self):
        """Cleanup method to close the session"""
        try:
            self.session.close()
        except:
            pass 