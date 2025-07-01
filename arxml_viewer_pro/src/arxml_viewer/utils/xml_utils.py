# src/arxml_viewer/utils/xml_utils.py
"""
XML Utilities - Helper functions for XML processing and namespace handling
"""

from typing import Dict, List, Optional, Any
from lxml import etree
from loguru import logger

class XMLNamespaceHandler:
    """
    Handles AUTOSAR XML namespaces and provides convenient XML operations
    """
    
    def __init__(self):
        self.namespaces: Dict[str, str] = {}
        self.default_namespace: Optional[str] = None
        
    def extract_namespaces(self, root: etree.Element):
        """Extract namespaces from XML root element"""
        self.namespaces = root.nsmap.copy() if root.nsmap else {}
        
        # Handle default namespace
        if None in self.namespaces:
            self.default_namespace = self.namespaces[None]
            # Add default namespace with 'ar' prefix for XPath queries
            self.namespaces['ar'] = self.default_namespace
            
        logger.debug(f"Extracted namespaces: {self.namespaces}")
    
    def find_element(self, parent: etree.Element, xpath: str) -> Optional[etree.Element]:
        """Find single element using XPath with namespace support"""
        try:
            elements = parent.xpath(self._prepare_xpath(xpath), namespaces=self.namespaces)
            return elements[0] if elements else None
        except Exception as e:
            logger.debug(f"XPath query failed: {xpath}, error: {e}")
            return None
    
    def find_elements(self, parent: etree.Element, xpath: str) -> List[etree.Element]:
        """Find multiple elements using XPath with namespace support"""
        try:
            return parent.xpath(self._prepare_xpath(xpath), namespaces=self.namespaces)
        except Exception as e:
            logger.debug(f"XPath query failed: {xpath}, error: {e}")
            return []
    
    def get_text(self, parent: etree.Element, xpath: str, default: str = "") -> str:
        """Get text content of element using XPath"""
        element = self.find_element(parent, xpath)
        if element is not None and element.text:
            return element.text.strip()
        return default
    
    def get_attribute(self, parent: etree.Element, xpath: str, attr_name: str, default: str = "") -> str:
        """Get attribute value of element using XPath"""
        element = self.find_element(parent, xpath)
        if element is not None:
            return element.get(attr_name, default)
        return default
    
    def _prepare_xpath(self, xpath: str) -> str:
        """Prepare XPath for namespace-aware queries"""
        if self.default_namespace and not xpath.startswith('.//'):
            # Add default namespace prefix to unqualified element names
            # This is a simple implementation - could be more sophisticated
            if '/' in xpath and not ':' in xpath:
                parts = xpath.split('/')
                qualified_parts = []
                for part in parts:
                    if part and not part.startswith('@') and not part.startswith('*'):
                        if '[' in part:
                            # Handle predicates like ELEMENT[condition]
                            element_name = part.split('[')[0]
                            predicate = part[part.find('['):]
                            if element_name and not element_name.startswith('.'):
                                qualified_parts.append(f"ar:{element_name}{predicate}")
                            else:
                                qualified_parts.append(part)
                        else:
                            if not part.startswith('.'):
                                qualified_parts.append(f"ar:{part}")
                            else:
                                qualified_parts.append(part)
                    else:
                        qualified_parts.append(part)
                return '/'.join(qualified_parts)
        return xpath

class XMLValidator:
    """
    XML validation utilities for ARXML files
    """
    
    @staticmethod
    def is_valid_xml(file_path: str) -> bool:
        """Check if file is valid XML"""
        try:
            etree.parse(file_path)
            return True
        except etree.XMLSyntaxError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def is_autosar_xml(file_path: str) -> bool:
        """Check if XML file appears to be AUTOSAR format"""
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            # Check for AUTOSAR root element
            root_name = etree.QName(root).localname
            if root_name in ['AUTOSAR', 'MSRSW']:
                return True
                
            # Check for AUTOSAR namespace
            if any('autosar' in ns.lower() for ns in root.nsmap.values() if ns):
                return True
                
            return False
            
        except Exception:
            return False
    
    @staticmethod
    def get_xml_info(file_path: str) -> Dict[str, Any]:
        """Get basic XML file information"""
        try:
            tree = etree.parse(file_path)
            root = tree.getroot()
            
            return {
                'valid': True,
                'root_element': etree.QName(root).localname,
                'namespace': etree.QName(root).namespace,
                'encoding': tree.docinfo.encoding,
                'xml_version': tree.docinfo.xml_version,
                'namespaces': root.nsmap,
                'element_count': len(tree.getroot().xpath('//*'))
            }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }