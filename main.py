#!/usr/bin/env python3

import asyncio
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Confirm, Prompt
from rich.panel import Panel
from rich.text import Text
import typer

from kalki.modules.vision import VisionSystem
from kalki.modules.actions import ActionEngine
from kalki.modules.commands import CommandProcessor
from kalki.modules.jan_client import JanClient

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True),
        logging.FileHandler("logs/kalki.log")
    ]
)
logger = logging.getLogger("kalki")

def print_banner(console: Console):
    """Print the Kalki banner"""
    banner = Text()
    banner.append("🤖 ", style="bold blue")
    banner.append("KALKI", style="bold cyan")
    banner.append(" - Your Local AI Assistant", style="bold white")
    console.print(Panel(banner, border_style="cyan"))

async def main(
    jan_url: str = "http://0.0.0.0:8080",
    safe_mode: bool = True,
    auto_confirm: bool = False,
):
    """Kalki - A powerful local AI assistant"""
    try:
        # Initialize components
        console = Console()
        print_banner(console)
        
        # Initialize core systems
        vision = VisionSystem()
        actions = ActionEngine(safe_mode=safe_mode)
        jan = JanClient(base_url=jan_url)
        processor = CommandProcessor(jan, actions, vision)
        
        # Check Jan.ai connection
        try:
            await jan.check_connection()
            console.print("[bold green]✓ Connected to Jan.ai[/bold green]")
        except Exception as e:
            console.print("[bold red]✗ Could not connect to Jan.ai[/bold red]")
            console.print(f"Error: {str(e)}")
            console.print("\nMake sure Jan.ai is running and the API is enabled.")
            sys.exit(1)
        
        console.print(f"\nSafe mode: {'✅' if safe_mode else '❌'}")
        console.print(f"Auto-confirm: {'✅' if auto_confirm else '❌'}")
        
        console.print("\n[bold]Type your commands or 'exit' to quit[/bold]")
        console.print("Examples:")
        console.print("- 'Open Firefox'")
        console.print("- 'Click the login button'")
        console.print("- 'Type Hello World'")
        console.print()
        
        while True:
            try:
                # Get user input
                command = Prompt.ask("[bold cyan]You[/bold cyan]")
                
                if command.lower() in ['exit', 'quit']:
                    break
                    
                # Process command
                result = await processor.process_command(command)
                
                if result['success']:
                    console.print("[bold green]✓[/bold green]", result['message'])
                else:
                    console.print("[bold red]✗[/bold red]", result['message'])
                    if 'error' in result:
                        console.print(f"Error: {result['error']}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Command failed: {e}")
                console.print(f"[bold red]Error:[/bold red] {str(e)}")
        
        # Cleanup
        vision.close()
        console.print("\nGoodbye! 👋")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        console.print(f"[bold red]Fatal error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    typer.run(main) 