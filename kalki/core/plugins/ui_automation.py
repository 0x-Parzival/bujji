import pyautogui
from typing import Optional, Tuple
from .base import PluginInterface, PluginResult

class UIAutomationPlugin(PluginInterface):
    @property
    def name(self) -> str:
        return "ui_automation"
    
    @property
    def description(self) -> str:
        return "Provides UI automation capabilities like clicking, typing, and finding UI elements"
    
    async def execute(self, **kwargs) -> PluginResult:
        """Execute UI automation actions."""
        action = kwargs.get('action')
        if not action:
            return PluginResult(
                success=False,
                data=None,
                error="No action specified"
            )
        
        try:
            if action == "click":
                return await self._handle_click(**kwargs)
            elif action == "type":
                return await self._handle_type(**kwargs)
            elif action == "find":
                return await self._handle_find(**kwargs)
            else:
                return PluginResult(
                    success=False,
                    data=None,
                    error=f"Unknown action: {action}"
                )
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=str(e)
            )
    
    async def _handle_click(self, **kwargs) -> PluginResult:
        """Handle click actions."""
        x = kwargs.get('x')
        y = kwargs.get('y')
        
        if x is not None and y is not None:
            pyautogui.click(x=x, y=y)
            return PluginResult(
                success=True,
                data={"x": x, "y": y}
            )
        
        # Try to find and click by image
        image = kwargs.get('image')
        if image:
            try:
                location = pyautogui.locateCenterOnScreen(image, confidence=0.9)
                if location:
                    pyautogui.click(location)
                    return PluginResult(
                        success=True,
                        data={"location": location}
                    )
            except Exception as e:
                return PluginResult(
                    success=False,
                    data=None,
                    error=f"Failed to find image: {str(e)}"
                )
        
        return PluginResult(
            success=False,
            data=None,
            error="No valid click target specified"
        )
    
    async def _handle_type(self, **kwargs) -> PluginResult:
        """Handle typing actions."""
        text = kwargs.get('text')
        if not text:
            return PluginResult(
                success=False,
                data=None,
                error="No text specified"
            )
        
        interval = kwargs.get('interval', 0.1)
        pyautogui.write(text, interval=interval)
        return PluginResult(
            success=True,
            data={"text": text}
        )
    
    async def _handle_find(self, **kwargs) -> PluginResult:
        """Handle find element actions."""
        image = kwargs.get('image')
        if not image:
            return PluginResult(
                success=False,
                data=None,
                error="No image specified"
            )
        
        try:
            location = pyautogui.locateCenterOnScreen(image, confidence=0.9)
            if location:
                return PluginResult(
                    success=True,
                    data={"location": location}
                )
            return PluginResult(
                success=False,
                data=None,
                error="Element not found"
            )
        except Exception as e:
            return PluginResult(
                success=False,
                data=None,
                error=f"Failed to find element: {str(e)}"
            ) 