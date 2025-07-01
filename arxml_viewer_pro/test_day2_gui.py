#!/usr/bin/env python3
"""
Test script for Day 2 GUI implementation
Save as: test_day2_gui.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

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

def test_gui():
    """Test the GUI with sample data"""
    print("🚀 Starting Day 2 GUI Test...")
    
    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ARXML Viewer Pro - Day 2 Test")
    
    try:
        # Import GUI components
        from arxml_viewer.gui.main_window import MainWindow
        from arxml_viewer.config import ConfigManager
        
        print("✅ GUI imports successful")
        
        # Create config manager
        config_manager = ConfigManager()
        
        # Create main window  
        main_window = MainWindow()
        print("✅ MainWindow created")
        
        # Create test data
        test_packages = create_test_data()
        print(f"✅ Test data created: {len(test_packages)} packages")
        
        # Count components for verification
        total_components = sum(len(pkg.get_all_components()) for pkg in test_packages)
        print(f"✅ Total components: {total_components}")
        
        # Simulate file opening
        main_window.on_file_opened("test_data.arxml")
        print("✅ File opened simulation")
        
        # Load test data into GUI
        main_window.on_parsing_finished(test_packages, {
            'statistics': {
                'components_parsed': total_components,
                'ports_parsed': sum(comp.port_count for pkg in test_packages for comp in pkg.get_all_components()),
                'parse_time': 0.123
            }
        })
        print("✅ Test data loaded into GUI")
        
        # Show window
        main_window.show()
        main_window.raise_()
        print("✅ MainWindow displayed")
        
        print("\n🎉 Day 2 GUI Test Ready!")
        print("=" * 50)
        print("You should see:")
        print("• Professional dark theme interface")
        print("• Three panels: Tree | Diagram | Properties") 
        print("• Color-coded components in the diagram")
        print("• Interactive component selection")
        print("• Zoom and pan functionality")
        print("=" * 50)
        print("💡 Try clicking on components to see their properties!")
        print("💡 Use mouse wheel to zoom, drag to pan")
        print("💡 Click 'Fit to Window' to reset view")
        
        # Run application
        return app.exec()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all Day 2 files are created:")
        print("• src/arxml_viewer/gui/main_window.py")
        print("• src/arxml_viewer/gui/graphics/graphics_scene.py")
        print("• src/arxml_viewer/gui/graphics/__init__.py")
        return 1
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

def check_files():
    """Check if required files exist"""
    required_files = [
        "src/arxml_viewer/gui/main_window.py",
        "src/arxml_viewer/gui/graphics/graphics_scene.py", 
        "src/arxml_viewer/gui/graphics/__init__.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing required files:")
        for file_path in missing_files:
            print(f"   • {file_path}")
        print("\nPlease create these files with the Day 2 implementation code.")
        return False
    
    print("✅ All required files present")
    return True

if __name__ == "__main__":
    print("🔍 Day 2 GUI Test - ARXML Viewer Pro")
    print("=" * 50)
    
    # Check files first
    if not check_files():
        sys.exit(1)
    
    # Run GUI test
    exit_code = test_gui()
    
    if exit_code == 0:
        print("\n🎉 Day 2 GUI test completed successfully!")
    else:
        print("\n❌ Day 2 GUI test failed")
    
    sys.exit(exit_code)