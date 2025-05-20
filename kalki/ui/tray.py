import pystray
from PIL import Image
import os
from pathlib import Path
from ..config.config_manager import config
from ..config.logging_setup import logger

class KalkiTray:
    def __init__(self):
        self.icon = None
        self.setup_tray()
        
    def create_menu(self):
        """Create the system tray menu."""
        return pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Status", self.show_status),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start", self.start_kalki),
            pystray.MenuItem("Stop", self.stop_kalki),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.quit_app)
        )
    
    def setup_tray(self):
        """Initialize the system tray icon."""
        try:
            # TODO: Replace with actual icon
            icon_path = Path(__file__).parent / "assets" / "icon.png"
            if not icon_path.exists():
                # Create a simple colored square as fallback
                img = Image.new('RGB', (64, 64), color='purple')
                img.save(icon_path)
            
            self.icon = pystray.Icon(
                "Kalki",
                Image.open(icon_path),
                "Kalki AI Assistant",
                self.create_menu()
            )
            logger.info("System tray initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize system tray: {e}")
    
    def show_window(self):
        """Show the main Kalki window."""
        logger.info("Show window requested")
        # TODO: Implement window show logic
    
    def show_status(self):
        """Show Kalki's current status."""
        logger.info("Status check requested")
        # TODO: Implement status check
    
    def start_kalki(self):
        """Start Kalki services."""
        logger.info("Starting Kalki services")
        # TODO: Implement start logic
    
    def stop_kalki(self):
        """Stop Kalki services."""
        logger.info("Stopping Kalki services")
        # TODO: Implement stop logic
    
    def quit_app(self):
        """Clean shutdown of the application."""
        logger.info("Shutting down Kalki")
        self.icon.stop()
        # TODO: Implement cleanup logic
    
    def run(self):
        """Run the system tray icon."""
        if config.get('ui.show_system_tray', True):
            self.icon.run()
        else:
            logger.info("System tray disabled in configuration") 