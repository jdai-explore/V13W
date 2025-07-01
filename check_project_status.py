#!/usr/bin/env python3
"""
Project Status Checker - Check what's implemented and what's next
"""

import sys
from pathlib import Path

def check_project_files():
    """Check what files exist in the project"""
    print("🔍 Checking Project Status...")
    print("=" * 50)
    
    current_dir = Path.cwd()
    print(f"📁 Current directory: {current_dir}")
    
    # Core implementation files to check
    files_to_check = {
        "Core Models": [
            "src/arxml_viewer/models/autosar.py",
            "src/arxml_viewer/models/component.py", 
            "src/arxml_viewer/models/port.py",
            "src/arxml_viewer/models/connection.py",
            "src/arxml_viewer/models/package.py"
        ],
        "Parsers": [
            "src/arxml_viewer/parsers/arxml_parser.py",
            "src/arxml_viewer/utils/xml_utils.py"
        ],
        "Core Application": [
            "src/arxml_viewer/core/application.py",
            "src/arxml_viewer/config.py",
            "src/arxml_viewer/main.py"
        ],
        "Utilities": [
            "src/arxml_viewer/utils/logger.py",
            "src/arxml_viewer/utils/constants.py"
        ],
        "Configuration": [
            "setup.py",
            "requirements.txt", 
            "requirements-dev.txt",
            "pytest.ini",
            "mypy.ini"
        ]
    }
    
    total_files = 0
    existing_files = 0
    
    for category, file_list in files_to_check.items():
        print(f"\n📋 {category}")
        print("-" * 30)
        
        for file_path in file_list:
            total_files += 1
            path = Path(file_path)
            if path.exists():
                size = path.stat().st_size
                print(f"✅ {file_path} ({size} bytes)")
                existing_files += 1
            else:
                print(f"❌ {file_path} (missing)")
    
    print(f"\n📊 Implementation Status: {existing_files}/{total_files} files exist")
    
    return existing_files, total_files

def check_imports():
    """Check if the implemented modules can be imported"""
    print("\n🔍 Testing Module Imports...")
    print("=" * 50)
    
    # Add src to path
    src_path = Path.cwd() / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    imports_to_test = [
        ("arxml_viewer", "Main package"),
        ("arxml_viewer.models.autosar", "AUTOSAR base models"),
        ("arxml_viewer.models.component", "Component models"),
        ("arxml_viewer.models.port", "Port models"),
        ("arxml_viewer.models.connection", "Connection models"),
        ("arxml_viewer.models.package", "Package models"),
        ("arxml_viewer.parsers.arxml_parser", "ARXML parser"),
        ("arxml_viewer.utils.xml_utils", "XML utilities"),
        ("arxml_viewer.utils.logger", "Logging utilities"),
        ("arxml_viewer.config", "Configuration"),
        ("arxml_viewer.core.application", "Core application")
    ]
    
    successful_imports = 0
    
    for module_name, description in imports_to_test:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
            successful_imports += 1
        except ImportError as e:
            print(f"❌ {module_name} - {description} (ImportError: {e})")
        except Exception as e:
            print(f"⚠️  {module_name} - {description} (Error: {e})")
    
    print(f"\n📊 Import Status: {successful_imports}/{len(imports_to_test)} modules importable")
    return successful_imports, len(imports_to_test)

def test_basic_functionality():
    """Test basic functionality of implemented components"""
    print("\n🔍 Testing Basic Functionality...")
    print("=" * 50)
    
    try:
        # Add src to path if not already added
        src_path = Path.cwd() / "src"
        if str(src_path) not in sys.path:
            sys.path.insert(0, str(src_path))
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Component model creation
        total_tests += 1
        try:
            from arxml_viewer.models.component import Component, ComponentType
            component = Component(
                short_name="TestComponent",
                component_type=ComponentType.APPLICATION
            )
            print("✅ Component model creation")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Component model creation: {e}")
        
        # Test 2: Port model creation
        total_tests += 1
        try:
            from arxml_viewer.models.port import Port, PortType
            port = Port(
                short_name="TestPort",
                port_type=PortType.PROVIDED
            )
            print("✅ Port model creation")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Port model creation: {e}")
        
        # Test 3: Package model creation
        total_tests += 1
        try:
            from arxml_viewer.models.package import Package
            package = Package(
                short_name="TestPackage",
                full_path="/Test/Package"
            )
            print("✅ Package model creation")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Package model creation: {e}")
        
        # Test 4: ARXML Parser instantiation
        total_tests += 1
        try:
            from arxml_viewer.parsers.arxml_parser import ARXMLParser
            parser = ARXMLParser()
            print("✅ ARXML parser instantiation")
            tests_passed += 1
        except Exception as e:
            print(f"❌ ARXML parser instantiation: {e}")
        
        # Test 5: Configuration manager
        total_tests += 1
        try:
            from arxml_viewer.config import ConfigManager
            config = ConfigManager()
            print("✅ Configuration manager")
            tests_passed += 1
        except Exception as e:
            print(f"❌ Configuration manager: {e}")
        
        print(f"\n📊 Functionality Status: {tests_passed}/{total_tests} tests passed")
        return tests_passed, total_tests
        
    except Exception as e:
        print(f"❌ Could not run functionality tests: {e}")
        return 0, 5

def determine_next_steps(file_status, import_status, func_status):
    """Determine what should be done next"""
    print("\n🎯 NEXT STEPS ANALYSIS")
    print("=" * 50)
    
    files_exist, total_files = file_status
    imports_work, total_imports = import_status
    funcs_work, total_funcs = func_status
    
    completion_percentage = ((files_exist / total_files) + 
                           (imports_work / total_imports) + 
                           (funcs_work / total_funcs)) / 3 * 100
    
    print(f"📊 Overall Completion: {completion_percentage:.1f}%")
    
    if completion_percentage >= 90:
        print("🎉 DAY 1 COMPLETE! Ready for Day 2")
        print("\n🚀 Day 2 Tasks:")
        print("1. Create PyQt6 MainWindow")
        print("2. Implement QGraphicsScene for component visualization")
        print("3. Add component rendering with color-coding")
        print("4. Implement zoom, pan, and selection")
        print("5. Create professional dark theme")
        
        print("\n💻 Start Day 2 with:")
        print("• Create src/arxml_viewer/gui/main_window.py")
        print("• Create src/arxml_viewer/gui/graphics/graphics_scene.py")
        print("• Test GUI: python -m arxml_viewer.main")
        
    elif completion_percentage >= 70:
        print("✅ DAY 1 MOSTLY COMPLETE - Minor fixes needed")
        print("\n🔧 Fix these issues:")
        if files_exist < total_files:
            print("• Complete missing implementation files")
        if imports_work < total_imports:
            print("• Fix import errors in modules")
        if funcs_work < total_funcs:
            print("• Debug functionality issues")
            
    elif completion_percentage >= 40:
        print("⚠️  DAY 1 PARTIALLY COMPLETE - Need more implementation")
        print("\n📋 Priority tasks:")
        print("1. Complete core data models")
        print("2. Implement ARXML parser")
        print("3. Fix import issues")
        print("4. Test basic functionality")
        
    else:
        print("❌ DAY 1 NEEDS SIGNIFICANT WORK")
        print("\n🏗️  Start with:")
        print("1. Create all model files")
        print("2. Implement basic parser structure")
        print("3. Set up proper imports")
        print("4. Run foundation tests")

def main():
    """Main status check function"""
    print("🔍 ARXML Viewer Pro - Project Status Check")
    print("=" * 60)
    
    # Check file existence
    file_status = check_project_files()
    
    # Check imports
    import_status = check_imports()
    
    # Test functionality
    func_status = test_basic_functionality()
    
    # Determine next steps
    determine_next_steps(file_status, import_status, func_status)
    
    print("\n" + "=" * 60)
    print("Status check complete! 📋✨")

if __name__ == "__main__":
    main()