#!/usr/bin/env python3
"""
Test ARXML Viewer Pro Application
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path.cwd() / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

def test_application():
    print("🧪 Testing ARXML Viewer Pro Application")
    print("=" * 50)
    
    try:
        # Test core imports
        from arxml_viewer.core.application import ARXMLViewerApplication
        from arxml_viewer.config import ConfigManager
        print("✅ Core application imports successfully")
        
        # Test configuration
        config_manager = ConfigManager()
        print("✅ Configuration manager created")
        
        # Test application creation (without GUI)
        print("🔧 Creating application (this may take a moment)...")
        app = ARXMLViewerApplication(
            config_manager=config_manager,
            show_splash=False
        )
        print("✅ Application created successfully")
        
        # Test if main window exists
        if hasattr(app, 'main_window') and app.main_window:
            print("✅ Main window created")
        else:
            print("⚠️  Main window not created (may need display)")
        
        print("\n🎉 Application core functionality works!")
        print("To run the full GUI application, use:")
        print("python -m arxml_viewer.main")
        
        return True
        
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_application()
