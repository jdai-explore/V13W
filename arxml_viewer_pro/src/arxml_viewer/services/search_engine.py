# src/arxml_viewer/services/search_engine.py
"""
Search Engine - SIMPLIFIED implementation for ARXML components
Basic text-based search functionality without complex dependencies
"""

import re
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass

class SearchScope(str, Enum):
    """Search scope options"""
    ALL = "all"
    COMPONENTS = "components"
    PORTS = "ports"
    PACKAGES = "packages"

class SearchMode(str, Enum):
    """Search mode options"""
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    EXACT = "exact"
    REGEX = "regex"
    FUZZY = "fuzzy"

@dataclass
class SearchResult:
    """Search result item"""
    item_name: str
    item_type: str
    item_uuid: str
    match_field: str
    relevance_score: float
    parent_package: Optional[str] = None
    match_text: Optional[str] = None

class SearchEngine:
    """
    SIMPLIFIED search engine for ARXML components
    Basic text matching without complex indexing
    """
    
    def __init__(self):
        self.indexed_items: List[Dict[str, Any]] = []
        self.packages: List[Any] = []
    
    def build_index(self, packages: List[Any]) -> None:
        """Build search index from packages"""
        self.packages = packages
        self.indexed_items.clear()
        
        try:
            for package in packages:
                # Index package itself
                self._index_item(package, "package", package.full_path if hasattr(package, 'full_path') else "")
                
                # Index components
                if hasattr(package, 'components'):
                    for component in package.components:
                        self._index_item(component, "component", package.full_path if hasattr(package, 'full_path') else "")
                        
                        # Index ports
                        if hasattr(component, 'all_ports'):
                            for port in component.all_ports:
                                self._index_item(port, "port", package.full_path if hasattr(package, 'full_path') else "")
                
                # Index sub-packages recursively
                if hasattr(package, 'sub_packages'):
                    self._index_sub_packages(package.sub_packages)
        
        except Exception as e:
            print(f"⚠️ Search index building failed: {e}")
    
    def _index_sub_packages(self, sub_packages: List[Any]) -> None:
        """Index sub-packages recursively"""
        for sub_package in sub_packages:
            try:
                self._index_item(sub_package, "package", sub_package.full_path if hasattr(sub_package, 'full_path') else "")
                
                if hasattr(sub_package, 'components'):
                    for component in sub_package.components:
                        self._index_item(component, "component", sub_package.full_path if hasattr(sub_package, 'full_path') else "")
                        
                        if hasattr(component, 'all_ports'):
                            for port in component.all_ports:
                                self._index_item(port, "port", sub_package.full_path if hasattr(sub_package, 'full_path') else "")
                
                if hasattr(sub_package, 'sub_packages'):
                    self._index_sub_packages(sub_package.sub_packages)
            except Exception:
                continue
    
    def _index_item(self, item: Any, item_type: str, package_path: str) -> None:
        """Index a single item"""
        try:
            item_data = {
                'object': item,
                'name': getattr(item, 'short_name', 'Unknown'),
                'type': item_type,
                'uuid': getattr(item, 'uuid', ''),
                'description': getattr(item, 'desc', ''),
                'package_path': package_path,
                'searchable_text': self._build_searchable_text(item)
            }
            self.indexed_items.append(item_data)
        except Exception:
            pass
    
    def _build_searchable_text(self, item: Any) -> str:
        """Build searchable text from item attributes"""
        try:
            text_parts = []
            
            # Add name
            if hasattr(item, 'short_name') and item.short_name:
                text_parts.append(item.short_name.lower())
            
            # Add description
            if hasattr(item, 'desc') and item.desc:
                text_parts.append(item.desc.lower())
            
            # Add component type if available
            if hasattr(item, 'component_type'):
                text_parts.append(str(item.component_type).lower())
            
            # Add port type if available
            if hasattr(item, 'port_type'):
                text_parts.append(str(item.port_type).lower())
            
            return ' '.join(text_parts)
        except Exception:
            return ''
    
    def search(self, query: str, scope: SearchScope = SearchScope.ALL, 
               mode: SearchMode = SearchMode.CONTAINS, max_results: int = 50) -> List[SearchResult]:
        """Perform search"""
        if not query.strip():
            return []
        
        results = []
        query_lower = query.lower().strip()
        
        try:
            for item_data in self.indexed_items:
                # Apply scope filter
                if scope != SearchScope.ALL:
                    if scope == SearchScope.COMPONENTS and item_data['type'] != 'component':
                        continue
                    elif scope == SearchScope.PORTS and item_data['type'] != 'port':
                        continue
                    elif scope == SearchScope.PACKAGES and item_data['type'] != 'package':
                        continue
                
                # Perform text matching
                match_score = self._calculate_match_score(query_lower, item_data, mode)
                
                if match_score > 0:
                    result = SearchResult(
                        item_name=item_data['name'],
                        item_type=item_data['type'],
                        item_uuid=item_data['uuid'],
                        match_field='name',
                        relevance_score=match_score,
                        parent_package=item_data['package_path'],
                        match_text=item_data['searchable_text']
                    )
                    results.append(result)
            
            # Sort by relevance score (descending)
            results.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Limit results
            if max_results > 0:
                results = results[:max_results]
            
            return results
        
        except Exception as e:
            print(f"⚠️ Search failed: {e}")
            return []
    
    def _calculate_match_score(self, query: str, item_data: Dict[str, Any], mode: SearchMode) -> float:
        """Calculate match score for an item"""
        try:
            name = item_data['name'].lower()
            searchable_text = item_data['searchable_text']
            
            if mode == SearchMode.EXACT:
                if name == query:
                    return 1.0
                elif query in searchable_text:
                    return 0.5
            
            elif mode == SearchMode.STARTS_WITH:
                if name.startswith(query):
                    return 0.9
                elif any(part.startswith(query) for part in searchable_text.split()):
                    return 0.6
            
            elif mode == SearchMode.ENDS_WITH:
                if name.endswith(query):
                    return 0.9
                elif any(part.endswith(query) for part in searchable_text.split()):
                    return 0.6
            
            elif mode == SearchMode.CONTAINS:
                if query in name:
                    return 0.8
                elif query in searchable_text:
                    return 0.5
            
            elif mode == SearchMode.REGEX:
                try:
                    if re.search(query, name):
                        return 0.8
                    elif re.search(query, searchable_text):
                        return 0.5
                except re.error:
                    # Invalid regex, fall back to contains
                    if query in name:
                        return 0.7
            
            elif mode == SearchMode.FUZZY:
                # Simple fuzzy matching - check if most characters match
                score = self._fuzzy_match_score(query, name)
                if score > 0.7:
                    return score * 0.8
                
                # Check words in searchable text
                for word in searchable_text.split():
                    word_score = self._fuzzy_match_score(query, word)
                    if word_score > 0.7:
                        return word_score * 0.6
            
            return 0.0
        
        except Exception:
            return 0.0
    
    def _fuzzy_match_score(self, query: str, text: str) -> float:
        """Simple fuzzy matching score"""
        try:
            if not query or not text:
                return 0.0
            
            query = query.lower()
            text = text.lower()
            
            if query == text:
                return 1.0
            
            if query in text:
                return 0.8
            
            # Count matching characters
            matches = 0
            for char in query:
                if char in text:
                    matches += 1
            
            return matches / len(query) if len(query) > 0 else 0.0
        
        except Exception:
            return 0.0
    
    def get_search_suggestions(self, query: str, max_suggestions: int = 10) -> List[str]:
        """Get search suggestions based on indexed items"""
        suggestions = set()
        query_lower = query.lower()
        
        try:
            for item_data in self.indexed_items:
                name = item_data['name']
                
                # Add names that start with query
                if name.lower().startswith(query_lower):
                    suggestions.add(name)
                
                # Add words from searchable text that start with query
                for word in item_data['searchable_text'].split():
                    if word.startswith(query_lower) and len(word) > len(query):
                        suggestions.add(word)
                
                if len(suggestions) >= max_suggestions:
                    break
            
            return sorted(list(suggestions))[:max_suggestions]
        
        except Exception:
            return []
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        try:
            type_counts = {}
            for item_data in self.indexed_items:
                item_type = item_data['type']
                type_counts[item_type] = type_counts.get(item_type, 0) + 1
            
            return {
                'total_indexed_items': len(self.indexed_items),
                'items_by_type': type_counts,
                'packages_indexed': len(self.packages)
            }
        except Exception:
            return {
                'total_indexed_items': 0,
                'items_by_type': {},
                'packages_indexed': 0
            }

# Export classes
__all__ = ['SearchEngine', 'SearchScope', 'SearchMode', 'SearchResult']