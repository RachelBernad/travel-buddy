"""Handler registry for easy extensibility and management."""

from typing import Dict, List, Type, Optional
from .base_handler import BaseHandler
from ..logger import logger


class HandlerRegistry:
    """Registry for managing and discovering handlers."""
    
    def __init__(self):
        self._handlers: Dict[str, Type[BaseHandler]] = {}
        self._instances: Dict[str, BaseHandler] = {}
    
    def register(self, handler_class: Type[BaseHandler], task_type: Optional[str] = None) -> None:
        """
        Register a handler class.
        
        Args:
            handler_class: The handler class to register
            task_type: Optional task type override (uses class default if not provided)
        """
        # Create a temporary instance to get the task type
        temp_instance = handler_class()
        actual_task_type = task_type or temp_instance.task_type
        
        if actual_task_type in self._handlers:
            raise ValueError(f"Handler for task type '{actual_task_type}' is already registered")
        
        self._handlers[actual_task_type] = handler_class
        logger.info(
            "Handler registered",
            task_type=actual_task_type,
            class_name=handler_class.__name__,
            description=temp_instance.description
        )
    
    def unregister(self, task_type: str) -> None:
        """Unregister a handler by task type."""
        if task_type in self._handlers:
            del self._handlers[task_type]
            if task_type in self._instances:
                del self._instances[task_type]
            logger.info("Handler unregistered", task_type=task_type)
        else:
            raise ValueError(f"No handler registered for task type: {task_type}")
    
    def get_handler(self, task_type: str) -> BaseHandler:
        """Get a handler instance by task type."""
        if task_type not in self._handlers:
            raise ValueError(f"No handler registered for task type: {task_type}")
        
        # Create instance if it doesn't exist (singleton pattern)
        if task_type not in self._instances:
            handler_class = self._handlers[task_type]
            self._instances[task_type] = handler_class()
            logger.info("Handler instance created", task_type=task_type, class_name=handler_class.__name__)
        
        return self._instances[task_type]
    
    def list_handlers(self) -> List[str]:
        """List all registered handler types."""
        return list(self._handlers.keys())
    
    def get_handler_info(self, task_type: str) -> Dict[str, str]:
        """Get information about a registered handler."""
        if task_type not in self._handlers:
            raise ValueError(f"No handler registered for task type: {task_type}")
        
        handler_class = self._handlers[task_type]
        instance = self.get_handler(task_type)
        
        return {
            "task_type": task_type,
            "class_name": handler_class.__name__,
            "description": instance.description,
            "module": handler_class.__module__
        }
    
    def create_all_handlers(self) -> List[BaseHandler]:
        """Create instances of all registered handlers."""
        handlers = []
        for task_type in self._handlers:
            handlers.append(self.get_handler(task_type))
        return handlers
    
    def is_registered(self, task_type: str) -> bool:
        """Check if a handler is registered for the given task type."""
        return task_type in self._handlers


# Global registry instance
registry = HandlerRegistry()


def register_handler(handler_class: Type[BaseHandler], task_type: Optional[str] = None) -> None:
    """Convenience function to register a handler."""
    registry.register(handler_class, task_type)


def get_handler(task_type: str) -> BaseHandler:
    """Convenience function to get a handler."""
    return registry.get_handler(task_type)


def list_handlers() -> List[str]:
    """Convenience function to list all handlers."""
    return registry.list_handlers()


def auto_register_handlers() -> None:
    """Auto-register all built-in handlers."""
    from travel_buddy.handlers.taskHandlers.destination_handler import DestinationHandler
    from travel_buddy.handlers.taskHandlers.attractions_handler import AttractionsHandler
    from travel_buddy.handlers.taskHandlers.packing_handler import PackingHandler
    from travel_buddy.handlers.taskHandlers.other_handler import OtherHandler
    
    # Register built-in handlers
    registry.register(DestinationHandler)
    registry.register(AttractionsHandler)
    registry.register(PackingHandler)
    registry.register(OtherHandler)
    
    logger.info(
        "Auto-registration completed",
        handler_count=len(registry.list_handlers()),
        handlers=registry.list_handlers()
    )


# Auto-register handlers when module is imported
auto_register_handlers()
