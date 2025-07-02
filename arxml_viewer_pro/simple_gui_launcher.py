#!/usr/bin/env python
"""
Simple GUI Launcher - Launch just the main window GUI directly
This bypasses the full application architecture and launches the GUI directly
Save as: simple_gui_launcher.py
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the ARXML Viewer Pro GUI directly"""
    print("🚀 ARXML Viewer Pro - Simple GUI Launcher")
    print("=" * 50)
    
    try:
        # Test environment first
        print(f"✅ Using Python: {sys.executable}")
        
        # Test PyQt5
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt, PYQT_VERSION_STR
        print(f"✅ PyQt5 {PYQT_VERSION_STR} available")
        
        # Create Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("ARXML Viewer Pro")
        
        # Import and create main window directly
        from arxml_viewer.gui.main_window import MainWindow
        print("✅ Main window imported successfully")
        
        # Create main window
        main_window = MainWindow()
        print("✅ Main window created")
        
        # Simulate having test data (optional)
        try:
            from arxml_viewer.models.component import Component, ComponentType
            from arxml_viewer.models.port import Port, PortType
            from arxml_viewer.models.package import Package
            
            # Create test data
            sensor_comp = Component(
                short_name="SensorComponent",
                component_type=ComponentType.APPLICATION,
                desc="Temperature sensor component"
            )
            
            sensor_port = Port(
                short_name="TempDataOut",
                port_type=PortType.PROVIDED,
                component_uuid=sensor_comp.uuid
            )
            sensor_comp.add_port(sensor_port)
            
            controller_comp = Component(
                short_name="ControllerComponent",
                component_type=ComponentType.COMPOSITION,
                desc="Main control logic"
            )
            
            controller_in = Port(
                short_name="SensorDataIn",
                port_type=PortType.REQUIRED,
                component_uuid=controller_comp.uuid
            )
            controller_out = Port(
                short_name="ControlOut",
                port_type=PortType.PROVIDED,
                component_uuid=controller_comp.uuid
            )
            controller_comp.add_port(controller_in)
            controller_comp.add_port(controller_out)
            
            actuator_comp = Component(
                short_name="ActuatorComponent",
                component_type=ComponentType.SERVICE,
                desc="Motor actuator"
            )
            
            actuator_port = Port(
                short_name="ControlIn",
                port_type=PortType.REQUIRED,
                component_uuid=actuator_comp.uuid
            )
            actuator_comp.add_port(actuator_port)
            
            # Create package
            test_package = Package(
                short_name="DemoSystem",
                full_path="/Demo/System"
            )
            
            test_package.add_component(sensor_comp)
            test_package.add_component(controller_comp)
            test_package.add_component(actuator_comp)
            
            # Simulate file opening
            main_window.on_file_opened("demo_system.arxml")
            
            # Load test data
            main_window.on_parsing_finished([test_package], {
                'statistics': {
                    'components_parsed': 3,
                    'ports_parsed': 4,
                    'parse_time': 0.05
                }
            })
            
            print("✅ Demo data loaded into GUI")
            
        except Exception as e:
            print(f"⚠️  Could not load demo data: {e}")
            print("✅ GUI will start without demo data")
        
        # Show the main window
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
        print("✅ Main window displayed")
        print("")
        print("🎉 ARXML Viewer Pro GUI Launched Successfully!")
        print("=" * 50)
        print("You should see:")
        print("• Professional dark theme interface")
        print("• Three-panel layout: Tree | Diagram | Properties")
        print("• Menu bar with File, View, Help")
        print("• Toolbar with Open, zoom controls")
        print("• Status bar with file information")
        print("• Component visualization (if demo data loaded)")
        print("")
        print("💡 Try:")
        print("• File → Open to load an ARXML file")
        print("• View menu for zoom and panel controls")
        print("• Click components in the diagram")
        print("=" * 50)
        
        # Run the application
        exit_code = app.exec_()
        
        print(f"\n👋 ARXML Viewer Pro closed (exit code: {exit_code})")
        return exit_code
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you're using conda Python: python (not python3)")
        print("2. Verify PyQt5: python -c 'import PyQt5; print(\"OK\")'")
        print("3. Check source files exist in src/arxml_viewer/")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())