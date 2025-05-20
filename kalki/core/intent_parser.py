from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import json
from ..config.logging_setup import logger
from ..models.model_handler import ModelHandler

@dataclass
class Intent:
    """Represents a parsed user intent."""
    action: str
    parameters: Dict[str, Any]
    context: Dict[str, Any]
    confidence: float
    raw_text: str

class IntentParser:
    def __init__(self, model_handler: ModelHandler):
        self.model = model_handler
        
    async def parse(self, text: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        """Parse natural language into structured intent."""
        context = context or {}
        
        # Create a prompt that instructs the model to output structured JSON
        prompt = self._create_parsing_prompt(text, context)
        
        try:
            # Get model response
            response = await self.model.generate(prompt)
            
            # Parse the response into structured format
            parsed = self._parse_response(response)
            
            # Validate the parsed intent
            if not self._validate_intent(parsed):
                raise ValueError("Invalid intent structure")
            
            return Intent(
                action=parsed['action'],
                parameters=parsed['parameters'],
                context=parsed.get('context', {}),
                confidence=parsed.get('confidence', 0.0),
                raw_text=text
            )
            
        except Exception as e:
            logger.error(f"Failed to parse intent: {e}")
            # Return a fallback intent for error handling
            return Intent(
                action="error",
                parameters={"error": str(e)},
                context=context,
                confidence=0.0,
                raw_text=text
            )
    
    def _create_parsing_prompt(self, text: str, context: Dict[str, Any]) -> str:
        """Create a prompt for the model to parse intent."""
        return f"""
        Parse the following command into a structured intent.
        Command: {text}
        Current Context: {json.dumps(context)}
        
        Output a JSON object with:
        - action: The main action to perform
        - parameters: Any parameters needed
        - context: Additional context needed
        - confidence: How confident you are (0-1)
        
        Example format:
        {{
            "action": "open_application",
            "parameters": {{"name": "Chrome", "url": "https://example.com"}},
            "context": {{"current_app": "desktop"}},
            "confidence": 0.95
        }}
        
        Parse now:
        """
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the model's response into a dictionary."""
        try:
            # Find JSON-like structure in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON structure found in response")
            
            json_str = response[start:end]
            return json.loads(json_str)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from response: {e}")
            raise
    
    def _validate_intent(self, parsed: Dict[str, Any]) -> bool:
        """Validate that the parsed intent has all required fields."""
        required_fields = ['action', 'parameters']
        return all(field in parsed for field in required_fields)

    async def refine_intent(self, intent: Intent) -> Intent:
        """Refine an intent with additional context or clarification."""
        # TODO: Implement intent refinement logic
        # This could include:
        # - Adding missing parameters
        # - Resolving ambiguities
        # - Expanding shortcuts or aliases
        return intent 