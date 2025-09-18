"""Type definitions and enums for the travel buddy system."""

from enum import Enum


class Mode(Enum):
    """Available processing modes."""
    SMART = "smart"


class HandlerType(Enum):
    """Available handler types."""
    DESTINATION = "destination"
    ATTRACTIONS = "attractions"
    PACKING = "packing"
    OTHER = "other"


class InteractionType(Enum):
    """Types of user interactions."""
    SINGLE = "query"
    INTERACTIVE = "interactive"
    MEMORY = "memory"
