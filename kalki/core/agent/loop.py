from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import asyncio
from ...config.logging_setup import logger
from ..plugins.base import plugin_registry, PluginResult

class ThoughtType(Enum):
    TASK_PLANNING = "task_planning"
    ACTION_SELECTION = "action_selection"
    OBSERVATION = "observation"
    REFLECTION = "reflection"

@dataclass
class Thought:
    type: ThoughtType
    content: str
    
@dataclass
class Action:
    plugin: str
    parameters: Dict[str, Any]

@dataclass
class TaskState:
    goal: str
    completed: bool = False
    thoughts: List[Thought] = None
    last_action: Optional[Action] = None
    last_result: Optional[PluginResult] = None
    
    def __post_init__(self):
        if self.thoughts is None:
            self.thoughts = []

class AgentLoop:
    def __init__(self, model_client):
        self.model_client = model_client
        self.available_plugins = plugin_registry.list_plugins()
    
    async def execute_task(self, goal: str, max_steps: int = 10) -> TaskState:
        """Execute a task using the ReAct loop."""
        state = TaskState(goal=goal)
        steps = 0
        
        while not state.completed and steps < max_steps:
            # Think about the current state
            thought = await self._think(state)
            state.thoughts.append(thought)
            
            if thought.type == ThoughtType.TASK_PLANNING:
                # Break down the task if needed
                subtasks = await self._plan_subtasks(state)
                for subtask in subtasks:
                    await self.execute_task(subtask, max_steps=max_steps-steps)
            
            elif thought.type == ThoughtType.ACTION_SELECTION:
                # Select and execute an action
                action = await self._select_action(state)
                if action:
                    state.last_action = action
                    result = await plugin_registry.execute_plugin(
                        action.plugin,
                        **action.parameters
                    )
                    state.last_result = result
                    
                    # Observe the result
                    observation = await self._observe(state)
                    state.thoughts.append(observation)
            
            elif thought.type == ThoughtType.REFLECTION:
                # Reflect on progress and decide if task is complete
                state.completed = await self._reflect(state)
            
            steps += 1
        
        return state
    
    async def _think(self, state: TaskState) -> Thought:
        """Generate the next thought based on the current state."""
        # TODO: Implement proper prompting
        prompt = self._create_thinking_prompt(state)
        response = await self.model_client.generate(prompt)
        
        # Parse response to determine thought type and content
        # This is a simplified version - implement proper parsing
        if "plan" in response.lower():
            return Thought(ThoughtType.TASK_PLANNING, response)
        elif "action" in response.lower():
            return Thought(ThoughtType.ACTION_SELECTION, response)
        else:
            return Thought(ThoughtType.REFLECTION, response)
    
    async def _plan_subtasks(self, state: TaskState) -> List[str]:
        """Break down a complex task into subtasks."""
        # TODO: Implement proper task breakdown
        prompt = f"Break down the task: {state.goal}"
        response = await self.model_client.generate(prompt)
        return response.split('\n')  # Simplified parsing
    
    async def _select_action(self, state: TaskState) -> Optional[Action]:
        """Select the next action based on available plugins."""
        # TODO: Implement proper action selection
        prompt = self._create_action_prompt(state)
        response = await self.model_client.generate(prompt)
        
        # Parse response to get plugin and parameters
        # This is a simplified version - implement proper parsing
        if "click" in response.lower():
            return Action(
                plugin="ui_automation",
                parameters={"action": "click", "x": 100, "y": 100}
            )
        return None
    
    async def _observe(self, state: TaskState) -> Thought:
        """Observe the results of the last action."""
        if state.last_result:
            content = (
                f"Action {'succeeded' if state.last_result.success else 'failed'}: "
                f"{state.last_result.error if state.last_result.error else str(state.last_result.data)}"
            )
        else:
            content = "No observation available"
        
        return Thought(ThoughtType.OBSERVATION, content)
    
    async def _reflect(self, state: TaskState) -> bool:
        """Reflect on the current state and determine if the task is complete."""
        # TODO: Implement proper completion check
        prompt = self._create_reflection_prompt(state)
        response = await self.model_client.generate(prompt)
        return "complete" in response.lower()
    
    def _create_thinking_prompt(self, state: TaskState) -> str:
        """Create a prompt for the thinking phase."""
        return f"""
        Goal: {state.goal}
        Available plugins: {self.available_plugins}
        Previous thoughts: {state.thoughts}
        Last action: {state.last_action}
        Last result: {state.last_result}
        
        What should be done next? Consider:
        1. Does this need planning?
        2. Can we take a direct action?
        3. Should we reflect on progress?
        """
    
    def _create_action_prompt(self, state: TaskState) -> str:
        """Create a prompt for action selection."""
        return f"""
        Goal: {state.goal}
        Available plugins: {self.available_plugins}
        Current thought: {state.thoughts[-1] if state.thoughts else None}
        
        Select an action using available plugins.
        """
    
    def _create_reflection_prompt(self, state: TaskState) -> str:
        """Create a prompt for reflection."""
        return f"""
        Goal: {state.goal}
        Thoughts so far: {state.thoughts}
        Last action: {state.last_action}
        Last result: {state.last_result}
        
        Is this task complete? Why or why not?
        """ 