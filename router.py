from typing import Optional, Dict, Any
import logging
from model_handler import ModelHandler

class ModelRouter:
    def __init__(self, model_handler: ModelHandler):
        self.model = model_handler
        self.logger = logging.getLogger("kalki.router")
        
        # Keywords that suggest vision tasks
        self.vision_keywords = [
            "see", "look", "show", "image", "picture", "screen", 
            "describe", "what is in", "what's in", "visual"
        ]
        
    def choose_model(self, prompt: str, image_path: Optional[str] = None) -> str:
        """Choose appropriate model based on the task"""
        if image_path or any(keyword in prompt.lower() for keyword in self.vision_keywords):
            return "qwen:2.5"
        return "dolphin3"
        
    def route_task(self, 
                   prompt: str, 
                   image_path: Optional[str] = None,
                   **kwargs) -> Dict[Any, Any]:
        """
        Route the task to appropriate model and return response
        
        Args:
            prompt: The user's text prompt
            image_path: Optional path to image for visual tasks
            **kwargs: Additional parameters to pass to model API
        """
        try:
            model = self.choose_model(prompt, image_path)
            self.logger.info(f"Routing task to model: {model}")
            
            # Add system prompt for better task understanding
            system = """You are Kalki, an AI assistant that can control the computer.
            You can perform tasks like:
            - Opening applications and URLs
            - Clicking UI elements
            - Typing text
            - Running safe system commands
            
            When asked to perform an action, respond with:
            <action>command_type:details</action>
            
            Example actions:
            <action>open_url:https://google.com</action>
            <action>click:Login Button</action>
            <action>type:Hello World</action>
            <action>command:ls -l</action>
            """
            
            return self.model.generate(
                prompt=prompt,
                model=model,
                system=system,
                image_path=image_path,
                **kwargs
            )
            
        except Exception as e:
            self.logger.error(f"Error routing task: {str(e)}")
            raise 