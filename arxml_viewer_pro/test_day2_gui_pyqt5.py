#!/usr/bin/env python3
"""
Day 2 GUI Test - PyQt5 Version
Save as: test_day2_gui_pyqt5.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

# Use PyQt5 instead of PyQt6
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

def create_test_data():
    """Create test data for GUI demonstration"""
    from arxml_viewer.models.component import Component, ComponentType
    from arxml_viewer.models.port import Port, PortType
    from arxml_viewer.models.package import Package
    
    # Create test components
    sensor_comp = Component(
        short_name="SensorComponent",
        component_type=ComponentType.APPLICATION,
        desc="Temperature and pressure sensor component"
    )
    
    # Add ports to sensor
    sensor_port = Port(
        short_name="SensorDataOut", 
        port_type=PortType.PROVIDED,
        component_uuid=sensor_comp.uuid
    )
    sensor_comp.add_port(sensor_port)
    
    # Create controller component
    controller_comp = Component(
        short_name="ControllerComponent", 
        component_type=ComponentType.APPLICATION,
        desc="Main control logic component"
    )
    
    # Add ports to controller
    controller_in_port = Port(
        short_name="SensorDataIn",
        port_type=PortType.REQUIRED,
        component_uuid=controller_comp.uuid
    )
    controller_out_port = Port(
        short_name="ActuatorCmd",
        port_type=PortType.PROVIDED, 
        component_uuid=controller_comp.uuid
    )
    controller_comp.add_port(controller_in_port)
    controller_comp.add_port(controller_out_port)
    
    # Create actuator component
    actuator_comp = Component(
        short_name="ActuatorComponent",
        component_type=ComponentType.SERVICE,
        desc="Motor control actuator"
    )
    
    actuator_port = Port(
        short_name="ActuatorCmdIn",
        port_type=PortType.REQUIRED,
        component_uuid=actuator_comp.uuid
    )
    actuator_comp.add_port(actuator_port)
    
    # Create composition
    system_comp = Component(
        short_name="SystemComposition",
        component_type=ComponentType.COMPOSITION,
        desc="Complete control system"
    )
    
    # Add interface port to composition
    comp_port = Port(
        short_name="SystemInterface",
        port_type=PortType.PROVIDED,
        component_uuid=system_comp.uuid
    )
    system_comp.add_port(comp_port)
    
    # Create test package
    package = Package(
        short_name="TestSystem",
        full_path="/TestSystem"
    )
    
    package.add_component(sensor_comp)
    package.add_component(controller_comp) 
    package.add_component(actuator_comp)
    package.add_component(system_comp)
    
    return [package]

def test_gui_pyqt5():
    """Test the GUI with PyQt5"""
    print("🚀 Starting Day 2 GUI Test with PyQt5...")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ARXML Viewer Pro - Day 2 Test (PyQt5)")
    
    try:
        # Test basic PyQt5 functionality first
        from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt5.QtCore import Qt
        
        print("✅ PyQt5 imports successful")
        
        # Create a simple test window to verify PyQt5 works
        test_window = QMainWindow()
        test_window.setWindowTitle("PyQt5 Test - ARXML Viewer Pro")
        test_window.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        test_window.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        title_label = QLabel("🎉 PyQt5 is Working!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: green; padding: 20px;")
        layout.addWidget(title_label)
        
        info_label = QLabel("""
✅ GUI Framework: PyQt5
✅ Platform: macOS  
✅ Status: Ready for ARXML Viewer Pro

Next: We'll create the full GUI with:
• Component visualization
• Three-panel layout
• Interactive features
• Dark theme

Close this window to continue.
        """)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("font-size: 12px; padding: 20px;")
        layout.addWidget(info_label)
        
        # Show test window
        test_window.show()
        test_window.raise_()
        print("✅ PyQt5 test window displayed")
        
        print("\n🎉 PyQt5 GUI Test Success!")
        print("=" * 50)
        print("PyQt5 is working correctly on your macOS system!")
        print("This means we can build the full ARXML Viewer Pro GUI.")
        print("Close the test window to continue.")
        print("=" * 50)
        
        # Run the application
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return 1
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Main function"""
    print("🔍 Day 2 GUI Test - PyQt5 Version")
    print("=" * 50)
    
    # Test PyQt5 basic functionality
    try:
        from PyQt5.QtWidgets import QApplication
        print("✅ PyQt5 available")
    except ImportError:
        print("❌ PyQt5 not available")
        return 1
    
    # Run GUI test
    exit_code = test_gui_pyqt5()
    
    if exit_code == 0:
        print("\n🎉 PyQt5 test completed successfully!")
        print("Ready to create the full ARXML Viewer Pro GUI with PyQt5!")
    else:
        print("\n❌ PyQt5 test failed")
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())