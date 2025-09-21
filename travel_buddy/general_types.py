"""Type definitions and enums for the travel buddy system."""

from enum import Enum


class InteractionType(Enum):
    """Types of user interactions."""
    SINGLE = "query"
    INTERACTIVE = "interactive"
    MEMORY = "memory"
