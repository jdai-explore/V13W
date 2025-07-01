# src/arxml_viewer/models/autosar.py
"""
AUTOSAR Base Models - Core data structures for AUTOSAR elements
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import uuid4

class AutosarElement(BaseModel):
    """Base class for all AUTOSAR elements"""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    short_name: Optional[str] = None
    desc: Optional[str] = None
    category: Optional[str] = None
    
    class Config:
        """Pydantic configuration"""
        arbitrary_types_allowed = True
        validate_assignment = True
        use_enum_values = True