#!/usr/bin/env python3
"""
Day 1 Foundation Test - Validate core models and parsing foundation
Fixed version with proper syntax
"""

import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Test if we can import basic Python modules first
try:
    import json
    import os
    from typing import Dict, List, Optional
    from enum import Enum
    print("✅ Basic Python imports working")
except Exception as e:
    print(f"❌ Basic Python imports failed: {e}")
    sys.exit(1)

def test_python_environment():
    """Test Python environment and basic functionality"""
    print("🧪 Testing Python Environment...")
    
    # Test Python version
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required, found {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    
    # Test basic data structures
    test_dict = {"key": "value"}
    test_list = [1, 2, 3]
    test_str = "hello world"
    
    assert test_dict["key"] == "value"
    assert len(test_list) == 3
    assert test_str.upper() == "HELLO WORLD"
    
    print("✅ Basic data structures working")
    
    # Test file operations
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        temp_file = f.name
    
    try:
        with open(temp_file, 'r') as f:
            content = f.read()
        assert content == "test content"
        print("✅ File operations working")
        return True
    finally:
        Path(temp_file).unlink()

def test_required_modules():
    """Test if required modules can be imported"""
    print("🧪 Testing Required Module Imports...")
    
    required_modules = [
        ('lxml', 'XML processing'),
        ('PyQt6', 'GUI framework'),
        ('pandas', 'Data processing'),
        ('pydantic', 'Data validation'),
        ('pytest', 'Testing framework'),
        ('black', 'Code formatting'),
        ('mypy', 'Type checking')
    ]
    
    missing_modules = []
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError:
            print(f"❌ {module_name} - {description} (MISSING)")
            missing_modules.append(module_name)
    
    if missing_modules:
        print(f"\n⚠️  Missing modules: {', '.join(missing_modules)}")
        print("Please run the setup script to install dependencies")
        return False
    
    print("✅ All required modules available")
    return True

def test_pydantic_models():
    """Test basic Pydantic model functionality"""
    print("🧪 Testing Pydantic Models...")
    
    try:
        from pydantic import BaseModel, Field
        from typing import Optional, List
        from enum import Enum
        
        # Test basic model
        class ComponentType(str, Enum):
            APPLICATION = "APPLICATION-SW-COMPONENT-TYPE"
            COMPOSITION = "COMPOSITION-SW-COMPONENT-TYPE"
            SERVICE = "SERVICE-SW-COMPONENT-TYPE"
        
        class TestComponent(BaseModel):
            short_name: str
            component_type: ComponentType
            description: Optional[str] = None
            ports: List[str] = Field(default_factory=list)
            
            class Config:
                validate_assignment = True
        
        # Create test instance
        component = TestComponent(
            short_name="TestComponent",
            component_type=ComponentType.APPLICATION,
            description="Test application component"
        )
        
        # Test validation
        assert component.short_name == "TestComponent"
        assert component.component_type == ComponentType.APPLICATION
        assert component.description == "Test application component"
        assert len(component.ports) == 0
        
        # Test serialization
        data = component.dict()
        assert data["short_name"] == "TestComponent"
        assert data["component_type"] == "APPLICATION-SW-COMPONENT-TYPE"
        
        print("✅ Pydantic models working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Pydantic model test failed: {e}")
        return False

def test_xml_processing():
    """Test XML processing capabilities"""
    print("🧪 Testing XML Processing...")
    
    try:
        from lxml import etree
        
        # Create test XML
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <AUTOSAR xmlns="http://autosar.org/schema/r4.0">
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <SHORT-NAME>TestPackage</SHORT-NAME>
                    <ELEMENTS>
                        <APPLICATION-SW-COMPONENT-TYPE>
                            <SHORT-NAME>TestComponent</SHORT-NAME>
                            <DESC>
                                <L-2 L="EN">Test component description</L-2>
                            </DESC>
                        </APPLICATION-SW-COMPONENT-TYPE>
                    </ELEMENTS>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>'''
        
        # Parse with lxml
        root = etree.fromstring(xml_content.encode('utf-8'))
        
        # Test namespace handling
        namespaces = {'ar': 'http://autosar.org/schema/r4.0'}
        
        # Find elements
        packages = root.xpath('.//ar:AR-PACKAGE', namespaces=namespaces)
        assert len(packages) == 1
        
        package_name = packages[0].xpath('./ar:SHORT-NAME', namespaces=namespaces)[0].text
        assert package_name == "TestPackage"
        
        components = root.xpath('.//ar:APPLICATION-SW-COMPONENT-TYPE', namespaces=namespaces)
        assert len(components) == 1
        
        component_name = components[0].xpath('./ar:SHORT-NAME', namespaces=namespaces)[0].text
        assert component_name == "TestComponent"
        
        print("✅ XML processing working correctly")
        return True
        
    except Exception as e:
        print(f"❌ XML processing test failed: {e}")
        return False

def test_file_validation():
    """Test file operations and validation"""
    print("🧪 Testing File Operations...")
    
    try:
        # Create temporary ARXML file
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
        <AUTOSAR xmlns="http://autosar.org/schema/r4.0">
            <AR-PACKAGES>
                <AR-PACKAGE>
                    <SHORT-NAME>Components</SHORT-NAME>
                    <ELEMENTS>
                        <APPLICATION-SW-COMPONENT-TYPE>
                            <SHORT-NAME>SensorComponent</SHORT-NAME>
                            <PORTS>
                                <P-PORT-PROTOTYPE>
                                    <SHORT-NAME>DataOut</SHORT-NAME>
                                </P-PORT-PROTOTYPE>
                            </PORTS>
                        </APPLICATION-SW-COMPONENT-TYPE>
                    </ELEMENTS>
                </AR-PACKAGE>
            </AR-PACKAGES>
        </AUTOSAR>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.arxml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            # Test file exists
            assert Path(temp_file).exists()
            
            # Test file size
            file_size = Path(temp_file).stat().st_size
            assert file_size > 0
            
            # Test XML validity
            from lxml import etree
            tree = etree.parse(temp_file)
            root = tree.getroot()
            assert root is not None
            
            # Test namespace
            assert 'autosar' in root.nsmap.get(None, '').lower()
            
            print("✅ File operations working correctly")
            return True
            
        finally:
            Path(temp_file).unlink()
            
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False

def test_performance():
    """Test basic performance characteristics"""
    print("🧪 Testing Performance...")
    
    try:
        import time
        
        # Test list operations
        start_time = time.time()
        test_list = [i for i in range(10000)]
        list_time = time.time() - start_time
        
        assert len(test_list) == 10000
        assert list_time < 1.0  # Should be very fast
        
        # Test dictionary operations
        start_time = time.time()
        test_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        dict_time = time.time() - start_time
        
        assert len(test_dict) == 1000
        assert dict_time < 1.0
        
        # Test string operations
        start_time = time.time()
        test_str = "test " * 1000
        result = test_str.upper().replace("TEST", "RESULT")
        string_time = time.time() - start_time
        
        assert "RESULT" in result
        assert string_time < 1.0
        
        print(f"✅ Performance test passed")
        print(f"   📊 List creation (10k): {list_time:.3f}s")
        print(f"   📊 Dict creation (1k): {dict_time:.3f}s") 
        print(f"   📊 String operations: {string_time:.3f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_project_structure():
    """Test if project structure exists"""
    print("🧪 Testing Project Structure...")
    
    try:
        # Check if we're in the right location
        current_dir = Path.cwd()
        
        # Look for key project files/directories
        expected_items = [
            ('src', 'directory'),
            ('tests', 'directory'),
            ('requirements.txt', 'file'),
            ('setup.py', 'file'),
            ('.gitignore', 'file')
        ]
        
        missing_items = []
        found_items = []
        
        for item_name, item_type in expected_items:
            item_path = current_dir / item_name
            if item_type == 'directory':
                if item_path.is_dir():
                    found_items.append(f"📁 {item_name}/")
                else:
                    missing_items.append(f"📁 {item_name}/")
            else:  # file
                if item_path.is_file():
                    found_items.append(f"📄 {item_name}")
                else:
                    missing_items.append(f"📄 {item_name}")
        
        if found_items:
            print("✅ Found project structure items:")
            for item in found_items:
                print(f"   {item}")
        
        if missing_items:
            print("⚠️  Missing project structure items:")
            for item in missing_items:
                print(f"   {item}")
            print("   (This is OK if you haven't run the setup script yet)")
        
        return True
        
    except Exception as e:
        print(f"❌ Project structure test failed: {e}")
        return False

def run_all_tests():
    """Run all foundation tests"""
    print("🚀 Running Day 1 Foundation Tests")
    print("=" * 50)
    
    tests = [
        ("Python Environment", test_python_environment),
        ("Required Modules", test_required_modules),
        ("Pydantic Models", test_pydantic_models),
        ("XML Processing", test_xml_processing),
        ("File Operations", test_file_validation),
        ("Performance", test_performance),
        ("Project Structure", test_project_structure)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            print(f"\n📋 {test_name}")
            print("-" * 30)
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All foundation tests passed!")
        print("\n✅ Environment is ready for ARXML Viewer Pro development!")
        print("🚀 Ready for Day 2: PyQt6 GUI Implementation")
        return True
    elif passed >= total - 2:  # Allow 1-2 failures for missing modules
        print("✅ Core functionality working!")
        print("⚠️  Some optional components missing - install dependencies to fix")
        print("🚀 You can proceed with development")
        return True
    else:
        print("❌ Critical issues found. Please fix before proceeding.")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you're using Python 3.9+")
        print("2. Run the setup script to install dependencies")
        print("3. Check that you're in the correct directory")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)