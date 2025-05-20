import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from .config_manager import config

class KalkiLogger:
    _instance: Optional[logging.Logger] = None
    
    @classmethod
    def setup(cls) -> logging.Logger:
        """Set up and return the Kalki logger instance."""
        if cls._instance is not None:
            return cls._instance
            
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Get configuration
        log_level = getattr(logging, config.get('system.log_level', 'INFO'))
        log_file = config.get('system.log_file', 'logs/kalki.log')
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Set up file handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10_000_000,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        
        # Set up console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Configure logger
        logger = logging.getLogger('kalki')
        logger.setLevel(log_level)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        cls._instance = logger
        return logger

# Global logger instance
logger = KalkiLogger.setup() 