# src/arxml_viewer/models/autosar.py - COMPATIBILITY FALLBACK
"""
AUTOSAR Base Classes - COMPATIBILITY FALLBACK ONLY
This file provides minimal compatibility for any remaining imports
All models have been converted to use dataclasses instead
"""

import uuid
from typing import Optional
from dataclasses import dataclass

@dataclass
class AutosarElement:
    """
    COMPATIBILITY FALLBACK for AutosarElement
    Minimal implementation for backward compatibility
    All models should use dataclasses directly instead
    """
    
    short_name: str = ""
    desc: Optional[str] = None
    uuid: str = ""
    
    def __post_init__(self):
        """Generate UUID if not provided"""
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
    
    def __str__(self) -> str:
        return f"AutosarElement({self.short_name})"
    
    def __repr__(self) -> str:
        return f"AutosarElement(short_name='{self.short_name}', uuid='{self.uuid}')"

# This class is deprecated - models should use dataclasses directly
__all__ = ['AutosarElement']

# Print warning when this module is imported
print("⚠️ WARNING: autosar.py is deprecated. Models should use dataclasses directly.")
print("   This compatibility fallback will be removed in future versions.")