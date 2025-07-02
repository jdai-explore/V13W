#!/usr/bin/env python
"""
Test Main Window Only - Simple test to launch just the main GUI window
Save as: test_main_window_only.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_main_window():
    """Test just the main window GUI"""
    print("🖥️  Testing Main Window GUI...")
    
    try:
        # Test PyQt5 first
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        print(f"✅ Using Python: {sys.executable}")
        print("✅ PyQt5 imports working")
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("ARXML Viewer Pro - GUI Test")
        
        # Import and create main window
        from arxml_viewer.gui.main_window import MainWindow
        print("✅ Main window import successful")
        
        # Create main window
        main_window = MainWindow()
        print("✅ Main window created")
        
        # Show window
        main_window.show()
        main_window.raise_()
        print("✅ Main window displayed")
        
        print("\n🎉 Main Window GUI Test Successful!")
        print("=" * 50)
        print("You should see the ARXML Viewer Pro main window with:")
        print("• Dark theme interface")
        print("• Three panels: Tree | Diagram | Properties")
        print("• Menu bar with File, View, Help")
        print("• Toolbar with controls")
        print("• Status bar at bottom")
        print("• Welcome message")
        print("=" * 50)
        
        # Run the application
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = test_main_window()
    print(f"\nMain window test {'PASSED' if exit_code == 0 else 'FAILED'}")
    sys.exit(exit_code)