import aiohttp
import json
from typing import Optional, Dict, Any
from ..config.config_manager import config
from ..config.logging_setup import logger
from functools import lru_cache

class JanAIClient:
    def __init__(self):
        self.base_url = "http://localhost:1337"  # Jan.ai default API endpoint
        self.model = config.get('model.default', 'mistral')
        self.fallback_model = config.get('model.fallback', 'llama2')
        
        # Model parameters
        self.temperature = config.get('model.temperature', 0.7)
        self.max_tokens = config.get('model.max_tokens', 2000)
    
    @lru_cache(maxsize=100)
    async def _cached_generate(self, prompt: str, **kwargs) -> str:
        """Cached version of text generation."""
        return await self.generate(prompt, use_cache=False, **kwargs)
    
    async def generate(self, prompt: str, use_cache: bool = True, **kwargs) -> str:
        """Generate text using Jan.ai API."""
        if use_cache:
            return await self._cached_generate(prompt, **kwargs)
        
        async with aiohttp.ClientSession() as session:
            try:
                # Try primary model first
                response = await self._generate_with_model(
                    session, self.model, prompt, **kwargs
                )
                if response:
                    return response
                
                # Fall back to secondary model if primary fails
                logger.warning(f"Primary model {self.model} failed, trying fallback {self.fallback_model}")
                response = await self._generate_with_model(
                    session, self.fallback_model, prompt, **kwargs
                )
                if response:
                    return response
                
                raise Exception("Both primary and fallback models failed")
                
            except Exception as e:
                logger.error(f"Error generating text: {e}")
                return ""
    
    async def _generate_with_model(
        self,
        session: aiohttp.ClientSession,
        model: str,
        prompt: str,
        **kwargs
    ) -> Optional[str]:
        """Generate text with a specific model."""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": kwargs.get('temperature', self.temperature),
            "max_tokens": kwargs.get('max_tokens', self.max_tokens),
        }
        
        try:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('text', '')
                else:
                    logger.error(f"Error from Jan.ai API: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error calling Jan.ai API: {e}")
            return None
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models from Jan.ai."""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}/api/models"
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Error listing models: {response.status}")
                        return {}
            except Exception as e:
                logger.error(f"Error accessing Jan.ai API: {e}")
                return {}
    
    def clear_cache(self):
        """Clear the generation cache."""
        self._cached_generate.cache_clear()

# Global Jan.ai client instance
jan_client = JanAIClient() 