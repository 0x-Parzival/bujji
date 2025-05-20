#!/usr/bin/env python3

import sys
import signal
import asyncio
from pathlib import Path
from threading import Event

# Add Kalki root to Python path
sys.path.append(str(Path(__file__).parent.parent))

from kalki.config.config_manager import config
from kalki.config.logging_setup import logger
from kalki.integrations.jan_client import jan_client
from kalki.core.agent.loop import AgentLoop
from kalki.core.plugins.ui_automation import UIAutomationPlugin
from kalki.core.plugins.base import plugin_registry

class KalkiAssistant:
    def __init__(self):
        self.shutdown_event = Event()
        self.agent = None
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        
        logger.info("Initializing Kalki AI Assistant")
    
    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received shutdown signal {signum}")
        self.shutdown_event.set()
    
    async def initialize_components(self):
        """Initialize all Kalki components."""
        try:
            # Register plugins
            plugin_registry.register(UIAutomationPlugin())
            
            # Initialize agent loop
            self.agent = AgentLoop(jan_client)
            
            logger.info("All components initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize components: {e}")
            return False
    
    async def run(self):
        """Main run loop for Kalki."""
        try:
            if not await self.initialize_components():
                return
            
            logger.info("Kalki is running")
            
            # Example task execution
            if self.agent:
                state = await self.agent.execute_task(
                    "Open the browser and navigate to jan.ai"
                )
                logger.info(f"Task execution completed: {state.completed}")
            
            # Wait for shutdown signal
            while not self.shutdown_event.is_set():
                await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"Kalki encountered an error: {e}")
        finally:
            logger.info("Kalki is shutting down")

async def main():
    """Entry point for Kalki."""
    kalki = KalkiAssistant()
    await kalki.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...") 