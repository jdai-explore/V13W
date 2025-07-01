# src/arxml_viewer/config.py
"""
Application Configuration - Centralized configuration management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger

class AppConfig(BaseModel):
    """Application configuration model"""
    
    # Application settings
    theme: str = "dark"
    language: str = "en"
    auto_save_layout: bool = True
    
    # Performance settings
    max_file_size_mb: int = 500
    enable_caching: bool = True
    cache_size_limit: int = 100
    
    # UI settings
    window_geometry: Optional[Dict[str, int]] = None
    splitter_sizes: Optional[Dict[str, int]] = None
    show_grid: bool = True
    show_tooltips: bool = True
    
    # Parser settings
    validate_xml: bool = True
    resolve_references: bool = True
    parse_timeout_seconds: int = 30
    
    # Recent files
    recent_files: list = Field(default_factory=list)
    max_recent_files: int = 10
    
    # Export settings
    default_export_format: str = "PNG"
    export_quality: int = 300  # DPI for raster exports
    
    class Config:
        """Pydantic configuration"""
        validate_assignment = True

class ConfigManager:
    """Manages application configuration persistence"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Use platform-appropriate config directory
            if os.name == 'nt':  # Windows
                self.config_dir = Path.home() / "AppData" / "Local" / "ARXMLViewerPro"
            else:  # Unix-like
                self.config_dir = Path.home() / ".config" / "arxml-viewer-pro"
        
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self._config = self.load_config()
    
    def load_config(self) -> AppConfig:
        """Load configuration from file or create default"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return AppConfig(**config_data)
            else:
                logger.info("No config file found, creating default configuration")
                return AppConfig()
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using default")
            return AppConfig()
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config.dict(), f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    @property
    def config(self) -> AppConfig:
        """Get current configuration"""
        return self._config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration values"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
        self.save_config()
    
    def add_recent_file(self, file_path: str) -> None:
        """Add file to recent files list"""
        file_path = str(Path(file_path).resolve())
        
        # Remove if already exists
        if file_path in self._config.recent_files:
            self._config.recent_files.remove(file_path)
        
        # Add to beginning
        self._config.recent_files.insert(0, file_path)
        
        # Limit size
        if len(self._config.recent_files) > self._config.max_recent_files:
            self._config.recent_files = self._config.recent_files[:self._config.max_recent_files]
        
        self.save_config()
    
    def remove_recent_file(self, file_path: str) -> None:
        """Remove file from recent files list"""
        file_path = str(Path(file_path).resolve())
        if file_path in self._config.recent_files:
            self._config.recent_files.remove(file_path)
            self.save_config()