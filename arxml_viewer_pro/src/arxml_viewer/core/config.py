"""
Configuration Manager for ARXML Viewer Pro
Handles application configuration and settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class UIConfig:
    """UI configuration settings"""
    theme: str = "dark"
    window_width: int = 1200
    window_height: int = 800
    font_size: int = 10
    show_tree: bool = True
    show_properties: bool = True
    auto_save_layout: bool = True


@dataclass
class SearchConfig:
    """Search configuration settings"""
    max_results: int = 100
    enable_regex: bool = True
    case_sensitive: bool = False
    search_scope_default: str = "all"
    auto_complete_min_chars: int = 2


@dataclass
class PerformanceConfig:
    """Performance configuration settings"""
    max_components_display: int = 1000
    enable_lazy_loading: bool = True
    cache_parsed_files: bool = True
    max_cache_size_mb: int = 100


@dataclass
class AppConfig:
    """Main application configuration"""
    ui: UIConfig = None
    search: SearchConfig = None
    performance: PerformanceConfig = None
    recent_files: list = None
    last_opened_file: str = ""
    
    def __post_init__(self):
        if self.ui is None:
            self.ui = UIConfig()
        if self.search is None:
            self.search = SearchConfig()
        if self.performance is None:
            self.performance = PerformanceConfig()
        if self.recent_files is None:
            self.recent_files = []


class ConfigurationManager:
    """
    Manages application configuration with file persistence
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.config_file = self.config_dir / "arxml_viewer_config.json"
        self.config = AppConfig()
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing config
        self.load_config()
        
        logger.info(f"Configuration manager initialized with config at: {self.config_file}")
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory"""
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home())) / "ARXMLViewerPro"
        elif os.name == 'posix':  # Unix/Linux/macOS
            config_dir = Path.home() / ".config" / "arxml_viewer_pro"
        else:
            config_dir = Path.home() / ".arxml_viewer_pro"
        
        return config_dir
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Update config from loaded data
                if 'ui' in config_data:
                    self.config.ui = UIConfig(**config_data['ui'])
                if 'search' in config_data:
                    self.config.search = SearchConfig(**config_data['search'])
                if 'performance' in config_data:
                    self.config.performance = PerformanceConfig(**config_data['performance'])
                
                # Simple fields
                self.config.recent_files = config_data.get('recent_files', [])
                self.config.last_opened_file = config_data.get('last_opened_file', "")
                
                logger.info("Configuration loaded successfully")
                return True
            else:
                logger.info("No existing configuration found, using defaults")
                return False
                
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            config_data = {
                'ui': asdict(self.config.ui),
                'search': asdict(self.config.search),
                'performance': asdict(self.config.performance),
                'recent_files': self.config.recent_files,
                'last_opened_file': self.config.last_opened_file
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def get_config(self) -> AppConfig:
        """Get current configuration"""
        return self.config
    
    def add_recent_file(self, file_path: str) -> None:
        """Add a file to recent files list"""
        if file_path in self.config.recent_files:
            self.config.recent_files.remove(file_path)
        
        self.config.recent_files.insert(0, file_path)
        
        # Limit to 10 recent files
        if len(self.config.recent_files) > 10:
            self.config.recent_files = self.config.recent_files[:10]
        
        self.config.last_opened_file = file_path
        self.save_config()


# Global configuration instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def get_config() -> AppConfig:
    """Get current application configuration"""
    return get_config_manager().get_config()
