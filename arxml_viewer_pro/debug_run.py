#!/usr/bin/env python3
# debug_run.py - Updated debug runner

import sys
import os
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def create_sample_arxml():
    """Create a sample ARXML file for testing"""
    sample_arxml = '''<?xml version="1.0" encoding="UTF-8"?>
<AUTOSAR xmlns="http://autosar.org/schema/r4.0" 
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <AR-PACKAGES>
    <AR-PACKAGE>
      <SHORT-NAME>DemoPackage</SHORT-NAME>
      <DESC>
        <L-2>Demo package for ARXML Viewer Pro</L-2>
      </DESC>
      <ELEMENTS>
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>SensorComponent</SHORT-NAME>
          <DESC>
            <L-2>Temperature sensor component</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>TemperatureOutput</SHORT-NAME>
              <DESC>
                <L-2>Temperature data output</L-2>
              </DESC>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>PowerInput</SHORT-NAME>
              <DESC>
                <L-2>Power supply input</L-2>
              </DESC>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </APPLICATION-SW-COMPONENT-TYPE>
        
        <APPLICATION-SW-COMPONENT-TYPE>
          <SHORT-NAME>ControllerComponent</SHORT-NAME>
          <DESC>
            <L-2>Temperature controller</L-2>
          </DESC>
          <PORTS>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>TemperatureInput</SHORT-NAME>
              <DESC>
                <L-2>Temperature data input</L-2>
              </DESC>
            </R-PORT-PROTOTYPE>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>ControlOutput</SHORT-NAME>
              <DESC>
                <L-2>Control signal output</L-2>
              </DESC>
            </P-PORT-PROTOTYPE>
          </PORTS>
        </APPLICATION-SW-COMPONENT-TYPE>
        
        <SERVICE-SW-COMPONENT-TYPE>
          <SHORT-NAME>DiagnosticsService</SHORT-NAME>
          <DESC>
            <L-2>System diagnostics service</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>DiagnosticsInterface</SHORT-NAME>
              <DESC>
                <L-2>Diagnostics interface</L-2>
              </DESC>
            </P-PORT-PROTOTYPE>
          </PORTS>
        </SERVICE-SW-COMPONENT-TYPE>
        
        <COMPOSITION-SW-COMPONENT-TYPE>
          <SHORT-NAME>TemperatureSystem</SHORT-NAME>
          <DESC>
            <L-2>Complete temperature control system</L-2>
          </DESC>
          <PORTS>
            <P-PORT-PROTOTYPE>
              <SHORT-NAME>SystemOutput</SHORT-NAME>
            </P-PORT-PROTOTYPE>
            <R-PORT-PROTOTYPE>
              <SHORT-NAME>SystemInput</SHORT-NAME>
            </R-PORT-PROTOTYPE>
          </PORTS>
        </COMPOSITION-SW-COMPONENT-TYPE>
      </ELEMENTS>
      
      <SUB-PACKAGES>
        <AR-PACKAGE>
          <SHORT-NAME>ActuatorPackage</SHORT-NAME>
          <DESC>
            <L-2>Actuator components package</L-2>
          </DESC>
          <ELEMENTS>
            <APPLICATION-SW-COMPONENT-TYPE>
              <SHORT-NAME>HeaterActuator</SHORT-NAME>
              <DESC>
                <L-2>Heating element actuator</L-2>
              </DESC>
              <PORTS>
                <R-PORT-PROTOTYPE>
                  <SHORT-NAME>ControlInput</SHORT-NAME>
                  <DESC>
                    <L-2>Control signal input</L-2>
                  </DESC>
                </R-PORT-PROTOTYPE>
                <P-PORT-PROTOTYPE>
                  <SHORT-NAME>StatusOutput</SHORT-NAME>
                  <DESC>
                    <L-2>Actuator status output</L-2>
                  </DESC>
                </P-PORT-PROTOTYPE>
              </PORTS>
            </APPLICATION-SW-COMPONENT-TYPE>
            
            <APPLICATION-SW-COMPONENT-TYPE>
              <SHORT-NAME>CoolerActuator</SHORT-NAME>
              <DESC>
                <L-2>Cooling element actuator</L-2>
              </DESC>
              <PORTS>
                <R-PORT-PROTOTYPE>
                  <SHORT-NAME>ControlInput</SHORT-NAME>
                </R-PORT-PROTOTYPE>
                <P-PORT-PROTOTYPE>
                  <SHORT-NAME>StatusOutput</SHORT-NAME>
                </P-PORT-PROTOTYPE>
              </PORTS>
            </APPLICATION-SW-COMPONENT-TYPE>
          </ELEMENTS>
        </AR-PACKAGE>
      </SUB-PACKAGES>
    </AR-PACKAGE>
  </AR-PACKAGES>
</AUTOSAR>'''
    
    sample_file = Path("demo_system.arxml")
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_arxml)
    
    print(f"✅ Created sample ARXML: {sample_file}")
    return sample_file

def debug_run():
    """Run application with debug output"""
    print("🔧 Starting ARXML Viewer Pro (Debug Mode)")
    print("=" * 50)
    
    try:
        # Test imports first
        print("Testing imports...")
        
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 imported")
        
        from arxml_viewer.config import ConfigManager
        print("✅ Config imported")
        
        from arxml_viewer.core.application import ARXMLViewerApplication
        print("✅ Application imported")
        
        # Create sample file
        sample_file = create_sample_arxml()
        
        # Create Qt application
        app = QApplication(sys.argv)
        print("✅ Qt Application created")
        
        # Create config manager
        config_manager = ConfigManager()
        print("✅ Config manager created")
        
        # Create main application
        arxml_app = ARXMLViewerApplication(
            config_manager=config_manager,
            show_splash=False
        )
        print("✅ ARXML Viewer application created")
        
        # Show main window
        arxml_app.show()
        print("✅ Main window displayed")
        
        print("\n" + "=" * 50)
        print("🎉 Application started successfully!")
        print("\nTo test ARXML loading:")
        print(f"1. File → Open → {sample_file}")
        print("2. Check the tree panel (left)")
        print("3. Check the graphics panel (center)")
        print("4. Check the properties panel (right)")
        print("\n" + "=" * 50)
        
        # Run application event loop
        exit_code = app.exec_()
        
        # Clean up
        if sample_file.exists():
            sample_file.unlink()
            print(f"✅ Cleaned up sample file: {sample_file}")
        
        print(f"Application exited with code: {exit_code}")
        return exit_code == 0
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nMissing dependencies. Install with:")
        print("pip install PyQt5 pydantic lxml loguru")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    dependencies = [
        ('PyQt5', 'PyQt5'),
        ('pydantic', 'pydantic'),
        ('lxml', 'lxml'),
        ('loguru', 'loguru'),
    ]
    
    missing = []
    
    for name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - MISSING")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Install them with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies available")
    return True

def main():
    """Main function"""
    print("🚀 ARXML Viewer Pro - Debug Launcher")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return False
    
    # Run the application
    return debug_run()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)