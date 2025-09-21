
import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional
from functools import wraps


class TravelBuddyLogger:
    
    def __init__(self, name: str = "travel_buddy", level: int = logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # Create console handler if none exists
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs) -> None:
        """Log info message with optional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {context}"
        self.logger.info(message)
    
    def debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {context}"
        self.logger.debug(message)
    
    def warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {context}"
        self.logger.warning(message)
    
    def error(self, message: str, **kwargs) -> None:
        """Log error message with optional context."""
        if kwargs:
            context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
            message = f"{message} | {context}"
        self.logger.error(message)


# Global logger instance
logger = TravelBuddyLogger()


def log_timing(operation_name: str, **context):
    """Decorator to log timing and context for operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Starting {operation_name}", **context)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(f"Completed {operation_name}", duration=f"{duration:.3f}s", **context)
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {operation_name}", duration=f"{duration:.3f}s", error=str(e), **context)
                raise
        return wrapper
    return decorator


def log_model_call(model_name: str, prompt_length: int, **params):
    """Log model call with specs and timing."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(
                f"Model call: {model_name}",
                prompt_length=prompt_length,
                **params
            )
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                response_length = len(result) if isinstance(result, str) else 0
                logger.info(
                    f"Model response: {model_name}",
                    duration=f"{duration:.3f}s",
                    response_length=response_length,
                    tokens_per_sec=f"{response_length/duration:.1f}" if duration > 0 else "0"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Model error: {model_name}",
                    duration=f"{duration:.3f}s",
                    error=str(e)
                )
                raise
        return wrapper
    return decorator


def log_handler_operation(handler_type: str):
    """Log handler operations with context."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.info(f"Handler started", handler_type=handler_type)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.info(
                    f"Handler completed",
                    handler_type=handler_type,
                    duration=f"{duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Handler failed",
                    handler_type=handler_type,
                    duration=f"{duration:.3f}s",
                    error=str(e)
                )
                raise
        return wrapper
    return decorator


def log_memory_access(operation: str):
    """Log memory access operations."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            logger.debug(f"Memory {operation}")
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(
                    f"Memory {operation} completed",
                    duration=f"{duration:.3f}s"
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                logger.error(
                    f"Memory {operation} failed",
                    duration=f"{duration:.3f}s",
                    error=str(e)
                )
                raise
        return wrapper
    return decorator
