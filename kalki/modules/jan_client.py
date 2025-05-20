import aiohttp
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class JanClient:
    def __init__(self, base_url: str = "http://0.0.0.0:8080", api_key: Optional[str] = None):
        """Initialize Jan.ai client"""
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json"
        }
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
            
    async def check_connection(self) -> bool:
        """Check if Jan.ai server is accessible"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/v1/models") as response:
                    if response.status == 200:
                        return True
                    raise ConnectionError(f"Jan.ai server returned status {response.status}")
        except Exception as e:
            logger.error(f"Failed to connect to Jan.ai: {e}")
            raise ConnectionError(f"Could not connect to Jan.ai server at {self.base_url}")
            
    async def generate(self, prompt: str, model: str = "mistral", **kwargs) -> Dict[str, Any]:
        """Generate text using Jan.ai model"""
        try:
            messages = [{"role": "user", "content": prompt}]
            
            data = {
                "messages": messages,
                "model": model,
                **kwargs
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=self.headers,
                    json=data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Jan.ai API error: {error_text}")
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise
            
    async def list_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/v1/models",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Failed to list models: {error_text}")
                        
                    return await response.json()
                    
        except Exception as e:
            logger.error(f"Failed to list models: {e}")
            raise 