# src/arxml_viewer/models/interface.py
"""
Interface Models - Day 4 Implementation
Complete AUTOSAR interface definitions with methods, data elements, and analysis
"""

from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from .autosar import AutosarElement

class InterfaceType(str, Enum):
    """AUTOSAR interface types"""
    SENDER_RECEIVER = "SENDER-RECEIVER-INTERFACE"
    CLIENT_SERVER = "CLIENT-SERVER-INTERFACE"
    TRIGGER = "TRIGGER-INTERFACE"
    MODE_SWITCH = "MODE-SWITCH-INTERFACE"
    NV_DATA = "NV-DATA-INTERFACE"

class ArgumentDirection(str, Enum):
    """Method argument directions"""
    IN = "IN"
    OUT = "OUT"
    INOUT = "INOUT"

class DataTypeCategory(str, Enum):
    """Data type categories"""
    PRIMITIVE = "PRIMITIVE"
    ARRAY = "ARRAY"
    RECORD = "RECORD"
    UNION = "UNION"
    ENUM = "ENUM"
    STRING = "STRING"

class DataType(BaseModel):
    """Data type definition"""
    name: str
    category: DataTypeCategory
    type_reference: Optional[str] = None
    size_bytes: Optional[int] = None
    description: Optional[str] = None
    
    # Complex type details
    elements: List['DataElement'] = Field(default_factory=list)  # For records/unions
    enum_values: List[str] = Field(default_factory=list)  # For enums
    array_size: Optional[int] = None  # For arrays
    
    def is_primitive(self) -> bool:
        """Check if this is a primitive type"""
        return self.category == DataTypeCategory.PRIMITIVE
    
    def is_complex(self) -> bool:
        """Check if this is a complex type"""
        return self.category in [DataTypeCategory.RECORD, DataTypeCategory.UNION, DataTypeCategory.ARRAY]
    
    def get_size_estimate(self) -> int:
        """Estimate size in bytes"""
        if self.size_bytes:
            return self.size_bytes
        
        # Basic size estimates
        size_map = {
            'uint8': 1, 'int8': 1, 'boolean': 1,
            'uint16': 2, 'int16': 2,
            'uint32': 4, 'int32': 4, 'float32': 4,
            'uint64': 8, 'int64': 8, 'float64': 8
        }
        
        name_lower = self.name.lower()
        for type_name, size in size_map.items():
            if type_name in name_lower:
                if self.category == DataTypeCategory.ARRAY and self.array_size:
                    return size * self.array_size
                return size
        
        return 4  # Default estimate

class DataElement(BaseModel):
    """Interface data element"""
    name: str
    data_type: DataType
    description: Optional[str] = None
    is_optional: bool = False
    default_value: Optional[Any] = None
    
    # Constraints
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    
    def get_type_name(self) -> str:
        """Get type name for display"""
        return self.data_type.name
    
    def is_primitive(self) -> bool:
        """Check if element has primitive type"""
        return self.data_type.is_primitive()

class MethodArgument(BaseModel):
    """Method argument definition"""
    name: str
    data_type: DataType
    direction: ArgumentDirection
    description: Optional[str] = None
    is_optional: bool = False
    default_value: Optional[Any] = None
    
    def is_input(self) -> bool:
        """Check if argument is input"""
        return self.direction in [ArgumentDirection.IN, ArgumentDirection.INOUT]
    
    def is_output(self) -> bool:
        """Check if argument is output"""
        return self.direction in [ArgumentDirection.OUT, ArgumentDirection.INOUT]

class InterfaceMethod(BaseModel):
    """Interface method definition"""
    name: str
    description: Optional[str] = None
    arguments: List[MethodArgument] = Field(default_factory=list)
    return_type: Optional[DataType] = None
    
    # Method properties
    is_asynchronous: bool = False
    is_fire_and_forget: bool = False
    timeout_ms: Optional[int] = None
    
    # Error handling
    possible_errors: List[str] = Field(default_factory=list)
    
    def get_input_arguments(self) -> List[MethodArgument]:
        """Get input arguments"""
        return [arg for arg in self.arguments if arg.is_input()]
    
    def get_output_arguments(self) -> List[MethodArgument]:
        """Get output arguments"""
        return [arg for arg in self.arguments if arg.is_output()]
    
    def get_signature(self) -> str:
        """Get method signature as string"""
        args_str = ", ".join([
            f"{arg.name}: {arg.data_type.name}" 
            for arg in self.arguments
        ])
        
        return_str = f" -> {self.return_type.name}" if self.return_type else ""
        
        return f"{self.name}({args_str}){return_str}"
    
    def get_complexity_score(self) -> float:
        """Calculate method complexity score"""
        score = 1.0  # Base complexity
        
        # Add complexity for arguments
        score += len(self.arguments) * 0.2
        
        # Add complexity for complex types
        for arg in self.arguments:
            if arg.data_type.is_complex():
                score += 0.5
        
        # Add complexity for async methods
        if self.is_asynchronous:
            score += 0.3
        
        # Add complexity for error handling
        score += len(self.possible_errors) * 0.1
        
        return score

class Interface(AutosarElement):
    """
    AUTOSAR Interface definition - Complete Day 4 implementation
    """
    interface_type: InterfaceType
    
    # Interface content
    methods: List[InterfaceMethod] = Field(default_factory=list)
    data_elements: List[DataElement] = Field(default_factory=list)
    
    # Metadata
    package_path: Optional[str] = None
    version: Optional[str] = None
    namespace: Optional[str] = None
    
    # Interface properties
    is_service_interface: bool = False
    is_legacy_interface: bool = False
    compatibility_version: Optional[str] = None
    
    # Documentation
    documentation: Optional[str] = None
    examples: List[str] = Field(default_factory=list)
    
    @validator('interface_type')
    def validate_interface_type(cls, v):
        """Validate interface type"""
        if isinstance(v, str):
            return InterfaceType(v)
        return v
    
    @property
    def method_count(self) -> int:
        """Get number of methods"""
        return len(self.methods)
    
    @property
    def data_element_count(self) -> int:
        """Get number of data elements"""
        return len(self.data_elements)
    
    @property
    def is_client_server(self) -> bool:
        """Check if this is a client-server interface"""
        return self.interface_type == InterfaceType.CLIENT_SERVER
    
    @property
    def is_sender_receiver(self) -> bool:
        """Check if this is a sender-receiver interface"""
        return self.interface_type == InterfaceType.SENDER_RECEIVER
    
    def get_method_by_name(self, name: str) -> Optional[InterfaceMethod]:
        """Find method by name"""
        for method in self.methods:
            if method.name == name:
                return method
        return None
    
    def get_data_element_by_name(self, name: str) -> Optional[DataElement]:
        """Find data element by name"""
        for element in self.data_elements:
            if element.name == name:
                return element
        return None
    
    def add_method(self, method: InterfaceMethod) -> None:
        """Add a method to the interface"""
        # Check for duplicate names
        if not self.get_method_by_name(method.name):
            self.methods.append(method)
    
    def add_data_element(self, element: DataElement) -> None:
        """Add a data element to the interface"""
        # Check for duplicate names
        if not self.get_data_element_by_name(element.name):
            self.data_elements.append(element)
    
    def get_complexity_score(self) -> float:
        """Calculate interface complexity score"""
        score = 1.0  # Base complexity
        
        # Add complexity for methods
        for method in self.methods:
            score += method.get_complexity_score()
        
        # Add complexity for data elements
        score += len(self.data_elements) * 0.3
        
        # Add complexity for complex data types
        for element in self.data_elements:
            if element.data_type.is_complex():
                score += 0.5
        
        return score
    
    def get_interface_summary(self) -> Dict[str, Any]:
        """Get interface summary for display"""
        return {
            'name': self.short_name,
            'type': self.interface_type.value,
            'methods': self.method_count,
            'data_elements': self.data_element_count,
            'complexity': round(self.get_complexity_score(), 2),
            'package': self.package_path,
            'description': self.desc
        }
    
    def get_detailed_info(self) -> Dict[str, Any]:
        """Get detailed interface information"""
        return {
            'basic_info': self.get_interface_summary(),
            'methods': [
                {
                    'name': method.name,
                    'signature': method.get_signature(),
                    'arguments': len(method.arguments),
                    'is_async': method.is_asynchronous,
                    'description': method.description
                }
                for method in self.methods
            ],
            'data_elements': [
                {
                    'name': element.name,
                    'type': element.get_type_name(),
                    'is_primitive': element.is_primitive(),
                    'is_optional': element.is_optional,
                    'description': element.description
                }
                for element in self.data_elements
            ],
            'statistics': self.get_interface_statistics()
        }
    
    def get_interface_statistics(self) -> Dict[str, Any]:
        """Get interface statistics"""
        stats = {
            'total_methods': len(self.methods),
            'total_data_elements': len(self.data_elements),
            'complexity_score': self.get_complexity_score()
        }
        
        # Method statistics
        if self.methods:
            method_complexities = [method.get_complexity_score() for method in self.methods]
            stats['method_stats'] = {
                'avg_complexity': sum(method_complexities) / len(method_complexities),
                'max_complexity': max(method_complexities),
                'min_complexity': min(method_complexities),
                'async_methods': sum(1 for method in self.methods if method.is_asynchronous),
                'total_arguments': sum(len(method.arguments) for method in self.methods)
            }
        
        # Data element statistics
        if self.data_elements:
            primitive_count = sum(1 for element in self.data_elements if element.is_primitive())
            stats['data_element_stats'] = {
                'primitive_types': primitive_count,
                'complex_types': len(self.data_elements) - primitive_count,
                'optional_elements': sum(1 for element in self.data_elements if element.is_optional),
                'estimated_size_bytes': sum(element.data_type.get_size_estimate() for element in self.data_elements)
            }
        
        return stats
    
    def validate_interface(self) -> List[str]:
        """Validate interface consistency and return issues"""
        issues = []
        
        # Check basic requirements
        if not self.short_name:
            issues.append("Interface missing short_name")
        
        if not self.interface_type:
            issues.append("Interface missing interface_type")
        
        # Type-specific validation
        if self.interface_type == InterfaceType.CLIENT_SERVER:
            if not self.methods:
                issues.append("Client-Server interface should have methods")
        elif self.interface_type == InterfaceType.SENDER_RECEIVER:
            if not self.data_elements:
                issues.append("Sender-Receiver interface should have data elements")
        
        # Check for name conflicts
        method_names = [method.name for method in self.methods]
        if len(method_names) != len(set(method_names)):
            issues.append("Duplicate method names found")
        
        element_names = [element.name for element in self.data_elements]
        if len(element_names) != len(set(element_names)):
            issues.append("Duplicate data element names found")
        
        # Validate methods
        for method in self.methods:
            if not method.name:
                issues.append(f"Method missing name")
            
            # Check argument names
            arg_names = [arg.name for arg in method.arguments]
            if len(arg_names) != len(set(arg_names)):
                issues.append(f"Method '{method.name}' has duplicate argument names")
        
        return issues
    
    def generate_documentation(self) -> str:
        """Generate comprehensive interface documentation"""
        doc_parts = []
        
        # Header
        doc_parts.append(f"# Interface: {self.short_name}")
        doc_parts.append(f"**Type:** {self.interface_type.value}")
        
        if self.desc:
            doc_parts.append(f"**Description:** {self.desc}")
        
        if self.package_path:
            doc_parts.append(f"**Package:** {self.package_path}")
        
        doc_parts.append("")
        
        # Summary
        summary = self.get_interface_summary()
        doc_parts.append("## Summary")
        doc_parts.append(f"- Methods: {summary['methods']}")
        doc_parts.append(f"- Data Elements: {summary['data_elements']}")
        doc_parts.append(f"- Complexity Score: {summary['complexity']}")
        doc_parts.append("")
        
        # Methods section
        if self.methods:
            doc_parts.append("## Methods")
            for method in self.methods:
                doc_parts.append(f"### {method.name}")
                
                if method.description:
                    doc_parts.append(f"**Description:** {method.description}")
                
                doc_parts.append(f"**Signature:** `{method.get_signature()}`")
                
                if method.arguments:
                    doc_parts.append("**Arguments:**")
                    for arg in method.arguments:
                        direction_str = f"({arg.direction.value})"
                        desc_str = f" - {arg.description}" if arg.description else ""
                        doc_parts.append(f"- `{arg.name}: {arg.data_type.name}` {direction_str}{desc_str}")
                
                if method.is_asynchronous:
                    doc_parts.append("**Note:** This is an asynchronous method")
                
                if method.possible_errors:
                    doc_parts.append("**Possible Errors:**")
                    for error in method.possible_errors:
                        doc_parts.append(f"- {error}")
                
                doc_parts.append("")
        
        # Data Elements section
        if self.data_elements:
            doc_parts.append("## Data Elements")
            for element in self.data_elements:
                doc_parts.append(f"### {element.name}")
                
                if element.description:
                    doc_parts.append(f"**Description:** {element.description}")
                
                doc_parts.append(f"**Type:** `{element.data_type.name}` ({element.data_type.category.value})")
                
                if element.is_optional:
                    doc_parts.append("**Optional:** Yes")
                
                if element.default_value is not None:
                    doc_parts.append(f"**Default Value:** `{element.default_value}`")
                
                if element.min_value is not None or element.max_value is not None:
                    constraints = []
                    if element.min_value is not None:
                        constraints.append(f"Min: {element.min_value}")
                    if element.max_value is not None:
                        constraints.append(f"Max: {element.max_value}")
                    doc_parts.append(f"**Constraints:** {', '.join(constraints)}")
                
                doc_parts.append("")
        
        # Statistics section
        stats = self.get_interface_statistics()
        doc_parts.append("## Statistics")
        doc_parts.append(f"- **Total Complexity:** {stats['complexity_score']:.2f}")
        
        if 'method_stats' in stats:
            method_stats = stats['method_stats']
            doc_parts.append(f"- **Average Method Complexity:** {method_stats['avg_complexity']:.2f}")
            doc_parts.append(f"- **Total Arguments:** {method_stats['total_arguments']}")
            if method_stats['async_methods'] > 0:
                doc_parts.append(f"- **Asynchronous Methods:** {method_stats['async_methods']}")
        
        if 'data_element_stats' in stats:
            data_stats = stats['data_element_stats']
            doc_parts.append(f"- **Estimated Size:** {data_stats['estimated_size_bytes']} bytes")
            doc_parts.append(f"- **Primitive Types:** {data_stats['primitive_types']}")
            doc_parts.append(f"- **Complex Types:** {data_stats['complex_types']}")
        
        return "\n".join(doc_parts)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export interface to dictionary for serialization"""
        return {
            'uuid': self.uuid,
            'short_name': self.short_name,
            'description': self.desc,
            'interface_type': self.interface_type.value,
            'package_path': self.package_path,
            'version': self.version,
            'methods': [
                {
                    'name': method.name,
                    'description': method.description,
                    'signature': method.get_signature(),
                    'is_asynchronous': method.is_asynchronous,
                    'arguments': [
                        {
                            'name': arg.name,
                            'type': arg.data_type.name,
                            'direction': arg.direction.value,
                            'description': arg.description
                        }
                        for arg in method.arguments
                    ]
                }
                for method in self.methods
            ],
            'data_elements': [
                {
                    'name': element.name,
                    'type': element.data_type.name,
                    'category': element.data_type.category.value,
                    'description': element.description,
                    'is_optional': element.is_optional
                }
                for element in self.data_elements
            ],
            'statistics': self.get_interface_statistics()
        }
    
    def __str__(self) -> str:
        return f"Interface({self.short_name}, {self.interface_type.value})"
    
    def __repr__(self) -> str:
        return (f"Interface(uuid='{self.uuid}', short_name='{self.short_name}', "
                f"type='{self.interface_type.value}', methods={self.method_count}, "
                f"elements={self.data_element_count})")

# Update forward references for recursive models
DataType.model_rebuild()
DataElement.model_rebuild()