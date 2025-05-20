from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from ...config.logging_setup import logger

@dataclass
class PluginResult:
    """Represents the result of a plugin execution."""
    success: bool
    data: Any
    error: Optional[str] = None

class PluginInterface(ABC):
    """Base interface that all plugins must implement."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The unique name of the plugin."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the plugin does."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> PluginResult:
        """Execute the plugin's main functionality."""
        pass

class PluginRegistry:
    """Central registry for all available plugins."""
    _instance = None
    _plugins: Dict[str, PluginInterface] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PluginRegistry, cls).__new__(cls)
        return cls._instance
    
    def register(self, plugin: PluginInterface) -> None:
        """Register a new plugin."""
        if plugin.name in self._plugins:
            logger.warning(f"Plugin {plugin.name} already registered, overwriting")
        self._plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name}")
    
    def get_plugin(self, name: str) -> Optional[PluginInterface]:
        """Get a plugin by name."""
        return self._plugins.get(name)
    
    def list_plugins(self) -> List[Dict[str, str]]:
        """List all registered plugins."""
        return [
            {"name": p.name, "description": p.description}
            for p in self._plugins.values()
        ]
    
    async def execute_plugin(self, name: str, **kwargs) -> PluginResult:
        """Execute a plugin by name."""
        plugin = self.get_plugin(name)
        if not plugin:
            return PluginResult(
                success=False,
                data=None,
                error=f"Plugin {name} not found"
            )
        
        try:
            return await plugin.execute(**kwargs)
        except Exception as e:
            logger.error(f"Error executing plugin {name}: {e}")
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )

# Global plugin registry instance
plugin_registry = PluginRegistry() 