import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from .actions import ActionEngine
from .vision import VisionSystem
from .jan_client import JanClient

logger = logging.getLogger(__name__)

@dataclass
class Command:
    """Represents a parsed command with its parameters"""
    action: str
    parameters: Dict[str, Any]
    raw_text: str
    confidence: float

class CommandProcessor:
    def __init__(self, jan_client: JanClient, action_engine: ActionEngine, vision_system: VisionSystem):
        self.jan = jan_client
        self.actions = action_engine
        self.vision = vision_system
        self.command_history: List[Command] = []
        
    async def process_command(self, text: str) -> Dict[str, Any]:
        """Process a natural language command"""
        try:
            # Parse command using Jan.ai
            parsed = await self._parse_command(text)
            
            # Execute the command
            result = await self._execute_command(parsed)
            
            # Store in history
            self.command_history.append(parsed)
            
            return {
                'success': True,
                'action': parsed.action,
                'result': result,
                'message': 'Command executed successfully'
            }
            
        except Exception as e:
            logger.error(f"Command processing failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process command'
            }
    
    async def _parse_command(self, text: str) -> Command:
        """Parse natural language into structured command"""
        prompt = f"""
        Parse this command into a structured format:
        "{text}"
        
        Return JSON with:
        - action: The main action to take
        - parameters: Required parameters
        - confidence: How confident the parsing is (0-1)
        """
        
        response = await self.jan.generate(prompt)
        
        try:
            parsed = response['choices'][0]['message']['content']
            # Convert to Command object
            return Command(
                action=parsed['action'],
                parameters=parsed['parameters'],
                raw_text=text,
                confidence=parsed.get('confidence', 0.0)
            )
        except Exception as e:
            logger.error(f"Failed to parse command: {e}")
            raise
            
    async def _execute_command(self, command: Command) -> Dict[str, Any]:
        """Execute a parsed command"""
        if command.action == 'open_app':
            return {'opened': self.actions.open_application(command.parameters['name'])}
            
        elif command.action == 'open_url':
            self.actions.open_url(command.parameters['url'])
            return {'opened_url': command.parameters['url']}
            
        elif command.action == 'click':
            if 'text' in command.parameters:
                # Try to find and click text
                text = command.parameters['text']
                found = self.vision.find_text_on_screen(text)
                if found:
                    self.actions.click(found[0]['x'], found[0]['y'])
                    return {'clicked': text}
                return {'error': f"Text '{text}' not found"}
            else:
                # Click at coordinates
                self.actions.click(
                    command.parameters['x'],
                    command.parameters['y']
                )
                return {'clicked_at': (command.parameters['x'], command.parameters['y'])}
                
        elif command.action == 'type':
            self.actions.type_text(command.parameters['text'])
            return {'typed': command.parameters['text']}
            
        else:
            raise ValueError(f"Unknown action: {command.action}")
            
    def get_command_history(self) -> List[Dict[str, Any]]:
        """Get list of previously executed commands"""
        return [
            {
                'action': cmd.action,
                'parameters': cmd.parameters,
                'text': cmd.raw_text
            }
            for cmd in self.command_history
        ] 