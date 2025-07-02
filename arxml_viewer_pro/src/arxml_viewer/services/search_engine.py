# src/arxml_viewer/services/search_engine.py
"""
Search Engine Service - Full-text search and indexing for ARXML components
Provides fast searching across components, ports, and packages
"""

import re
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from ..models.component import Component
from ..models.port import Port
from ..models.package import Package
from ..utils.logger import get_logger

class SearchScope(Enum):
    """Search scope options"""
    ALL = "all"
    COMPONENTS = "components"
    PORTS = "ports"
    PACKAGES = "packages"
    DESCRIPTIONS = "descriptions"

class SearchMode(Enum):
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
    item_type: str  # 'component', 'port', 'package'
    item_uuid: str
    item_name: str
    match_field: str  # 'short_name', 'desc', etc.
    match_text: str
    relevance_score: float
    parent_package: Optional[str] = None
    highlight_ranges: List[Tuple[int, int]] = None

class SearchIndex:
    """Search index for fast lookups"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        
        # Indexes
        self.component_index: Dict[str, Component] = {}
        self.port_index: Dict[str, Port] = {}
        self.package_index: Dict[str, Package] = {}
        
        # Text indexes for fast searching
        self.text_index: Dict[str, Set[str]] = {}  # word -> set of item_uuids
        self.reverse_index: Dict[str, Dict[str, str]] = {}  # item_uuid -> field -> text
        
        # Statistics
        self.total_components = 0
        self.total_ports = 0
        self.total_packages = 0
    
    def add_component(self, component: Component):
        """Add component to search index"""
        self.component_index[component.uuid] = component
        self.total_components += 1
        
        # Index text fields
        fields_to_index = {
            'short_name': component.short_name or '',
            'desc': component.desc or '',
            'component_type': component.component_type.value,
            'package_path': component.package_path or ''
        }
        
        self._index_item(component.uuid, 'component', fields_to_index)
    
    def add_port(self, port: Port):
        """Add port to search index"""
        self.port_index[port.uuid] = port
        self.total_ports += 1
        
        # Index text fields
        fields_to_index = {
            'short_name': port.short_name or '',
            'desc': port.desc or '',
            'port_type': port.port_type.value,
            'interface_ref': port.interface_ref or ''
        }
        
        self._index_item(port.uuid, 'port', fields_to_index)
    
    def add_package(self, package: Package):
        """Add package to search index"""
        self.package_index[package.uuid] = package
        self.total_packages += 1
        
        # Index text fields
        fields_to_index = {
            'short_name': package.short_name or '',
            'desc': package.desc or '',
            'full_path': package.full_path or ''
        }
        
        self._index_item(package.uuid, 'package', fields_to_index)
    
    def _index_item(self, item_uuid: str, item_type: str, fields: Dict[str, str]):
        """Index an item's text fields"""
        if item_uuid not in self.reverse_index:
            self.reverse_index[item_uuid] = {}
        
        self.reverse_index[item_uuid]['item_type'] = item_type
        
        for field_name, text in fields.items():
            if not text:
                continue
                
            # Store field text
            self.reverse_index[item_uuid][field_name] = text
            
            # Extract words for text index
            words = self._extract_words(text)
            for word in words:
                if word not in self.text_index:
                    self.text_index[word] = set()
                self.text_index[word].add(item_uuid)
    
    def _extract_words(self, text: str) -> Set[str]:
        """Extract searchable words from text"""
        # Convert to lowercase and split on non-alphanumeric
        words = re.findall(r'\w+', text.lower())
        
        # Add original text as single term
        word_set = set(words)
        word_set.add(text.lower())
        
        return word_set
    
    def clear(self):
        """Clear all indexes"""
        self.component_index.clear()
        self.port_index.clear()
        self.package_index.clear()
        self.text_index.clear()
        self.reverse_index.clear()
        self.total_components = 0
        self.total_ports = 0
        self.total_packages = 0

class SearchEngine:
    """Main search engine for ARXML components"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.index = SearchIndex()
        
        # Search history
        self.search_history: List[str] = []
        self.max_history = 50
    
    def build_index(self, packages: List[Package]):
        """Build search index from packages"""
        self.logger.info("Building search index...")
        
        self.index.clear()
        
        for package in packages:
            # Index package
            self.index.add_package(package)
            
            # Index all components recursively
            for component in package.get_all_components(recursive=True):
                self.index.add_component(component)
                
                # Index component ports
                for port in component.all_ports:
                    self.index.add_port(port)
        
        self.logger.info(f"Search index built: {self.index.total_components} components, "
                        f"{self.index.total_ports} ports, {self.index.total_packages} packages")
    
    def search(self, 
               query: str,
               scope: SearchScope = SearchScope.ALL,
               mode: SearchMode = SearchMode.CONTAINS,
               max_results: int = 100) -> List[SearchResult]:
        """
        Perform search query
        
        Args:
            query: Search query string
            scope: What to search in
            mode: How to match the query
            max_results: Maximum number of results
            
        Returns:
            List of search results sorted by relevance
        """
        if not query.strip():
            return []
        
        query = query.strip()
        self._add_to_history(query)
        
        self.logger.debug(f"Searching for '{query}' in {scope.value} using {mode.value}")
        
        results = []
        
        if mode == SearchMode.REGEX:
            results = self._search_regex(query, scope)
        elif mode == SearchMode.FUZZY:
            results = self._search_fuzzy(query, scope)
        else:
            results = self._search_text(query, scope, mode)
        
        # Sort by relevance score (highest first)
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit results
        if max_results > 0:
            results = results[:max_results]
        
        self.logger.debug(f"Found {len(results)} search results")
        return results
    
    def _search_text(self, query: str, scope: SearchScope, mode: SearchMode) -> List[SearchResult]:
        """Perform text-based search"""
        results = []
        query_lower = query.lower()
        
        # Find candidate items
        candidates = set()
        
        if mode == SearchMode.CONTAINS:
            # Find all words that contain the query
            for word in self.index.text_index:
                if query_lower in word:
                    candidates.update(self.index.text_index[word])
        else:
            # Extract query words
            query_words = self.index._extract_words(query)
            for word in query_words:
                if word in self.index.text_index:
                    candidates.update(self.index.text_index[word])
        
        # Score and filter candidates
        for item_uuid in candidates:
            if item_uuid not in self.index.reverse_index:
                continue
            
            item_data = self.index.reverse_index[item_uuid]
            item_type = item_data.get('item_type', '')
            
            # Apply scope filter
            if not self._matches_scope(item_type, scope):
                continue
            
            # Check each field for matches
            for field_name, field_text in item_data.items():
                if field_name == 'item_type':
                    continue
                
                if self._field_matches_query(field_text, query, mode):
                    # Calculate relevance score
                    score = self._calculate_relevance(field_text, query, field_name)
                    
                    # Create search result
                    result = SearchResult(
                        item_type=item_type,
                        item_uuid=item_uuid,
                        item_name=item_data.get('short_name', 'Unknown'),
                        match_field=field_name,
                        match_text=field_text,
                        relevance_score=score,
                        parent_package=item_data.get('package_path'),
                        highlight_ranges=self._find_highlight_ranges(field_text, query)
                    )
                    
                    results.append(result)
                    break  # Only one result per item
        
        return results
    
    def _search_regex(self, pattern: str, scope: SearchScope) -> List[SearchResult]:
        """Perform regex-based search"""
        results = []
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            self.logger.warning(f"Invalid regex pattern '{pattern}': {e}")
            return results
        
        # Search through all indexed items
        for item_uuid, item_data in self.index.reverse_index.items():
            item_type = item_data.get('item_type', '')
            
            if not self._matches_scope(item_type, scope):
                continue
            
            # Check each field
            for field_name, field_text in item_data.items():
                if field_name == 'item_type':
                    continue
                
                match = regex.search(field_text)
                if match:
                    score = self._calculate_relevance(field_text, pattern, field_name)
                    
                    result = SearchResult(
                        item_type=item_type,
                        item_uuid=item_uuid,
                        item_name=item_data.get('short_name', 'Unknown'),
                        match_field=field_name,
                        match_text=field_text,
                        relevance_score=score,
                        parent_package=item_data.get('package_path'),
                        highlight_ranges=[(match.start(), match.end())]
                    )
                    
                    results.append(result)
                    break
        
        return results
    
    def _search_fuzzy(self, query: str, scope: SearchScope) -> List[SearchResult]:
        """Perform fuzzy search (simple implementation)"""
        results = []
        query_lower = query.lower()
        
        # Simple fuzzy matching based on Levenshtein-like distance
        for item_uuid, item_data in self.index.reverse_index.items():
            item_type = item_data.get('item_type', '')
            
            if not self._matches_scope(item_type, scope):
                continue
            
            best_score = 0
            best_field = None
            best_text = None
            
            for field_name, field_text in item_data.items():
                if field_name == 'item_type':
                    continue
                
                # Simple fuzzy scoring
                field_lower = field_text.lower()
                score = self._fuzzy_score(query_lower, field_lower)
                
                if score > best_score:
                    best_score = score
                    best_field = field_name
                    best_text = field_text
            
            if best_score > 0.3:  # Threshold for fuzzy matching
                result = SearchResult(
                    item_type=item_type,
                    item_uuid=item_uuid,
                    item_name=item_data.get('short_name', 'Unknown'),
                    match_field=best_field,
                    match_text=best_text,
                    relevance_score=best_score,
                    parent_package=item_data.get('package_path')
                )
                
                results.append(result)
        
        return results
    
    def _matches_scope(self, item_type: str, scope: SearchScope) -> bool:
        """Check if item type matches search scope"""
        if scope == SearchScope.ALL:
            return True
        elif scope == SearchScope.COMPONENTS:
            return item_type == 'component'
        elif scope == SearchScope.PORTS:
            return item_type == 'port'
        elif scope == SearchScope.PACKAGES:
            return item_type == 'package'
        return True
    
    def _field_matches_query(self, field_text: str, query: str, mode: SearchMode) -> bool:
        """Check if field matches query according to mode"""
        field_lower = field_text.lower()
        query_lower = query.lower()
        
        if mode == SearchMode.CONTAINS:
            return query_lower in field_lower
        elif mode == SearchMode.STARTS_WITH:
            return field_lower.startswith(query_lower)
        elif mode == SearchMode.ENDS_WITH:
            return field_lower.endswith(query_lower)
        elif mode == SearchMode.EXACT:
            return field_lower == query_lower
        
        return False
    
    def _calculate_relevance(self, text: str, query: str, field_name: str) -> float:
        """Calculate relevance score for a match"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Base score
        score = 0.5
        
        # Exact match bonus
        if text_lower == query_lower:
            score += 0.5
        
        # Starts with bonus
        if text_lower.startswith(query_lower):
            score += 0.3
        
        # Field importance bonus
        field_weights = {
            'short_name': 1.0,
            'desc': 0.7,
            'full_path': 0.8,
            'component_type': 0.6,
            'port_type': 0.6
        }
        score *= field_weights.get(field_name, 0.5)
        
        # Length factor (shorter matches are more relevant)
        if len(text) > 0:
            length_factor = len(query) / len(text)
            score *= (0.5 + 0.5 * length_factor)
        
        return min(score, 1.0)
    
    def _fuzzy_score(self, query: str, text: str) -> float:
        """Simple fuzzy matching score"""
        if not query or not text:
            return 0.0
        
        # Simple character matching
        matches = 0
        for char in query:
            if char in text:
                matches += 1
        
        # Basic fuzzy score
        char_score = matches / len(query)
        
        # Substring bonus
        if query in text:
            char_score += 0.3
        
        return min(char_score, 1.0)
    
    def _find_highlight_ranges(self, text: str, query: str) -> List[Tuple[int, int]]:
        """Find character ranges to highlight in text"""
        ranges = []
        text_lower = text.lower()
        query_lower = query.lower()
        
        start = 0
        while True:
            pos = text_lower.find(query_lower, start)
            if pos == -1:
                break
            ranges.append((pos, pos + len(query)))
            start = pos + 1
        
        return ranges
    
    def _add_to_history(self, query: str):
        """Add query to search history"""
        if query in self.search_history:
            self.search_history.remove(query)
        
        self.search_history.insert(0, query)
        
        if len(self.search_history) > self.max_history:
            self.search_history = self.search_history[:self.max_history]
    
    def get_search_suggestions(self, partial_query: str, max_suggestions: int = 10) -> List[str]:
        """Get search suggestions based on partial query"""
        if not partial_query:
            return self.search_history[:max_suggestions]
        
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Add matching history items
        for query in self.search_history:
            if partial_lower in query.lower():
                suggestions.append(query)
        
        # Add matching indexed terms
        for word in self.index.text_index:
            if partial_lower in word and word not in suggestions:
                suggestions.append(word)
                if len(suggestions) >= max_suggestions:
                    break
        
        return suggestions[:max_suggestions]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get search index statistics"""
        return {
            'total_components': self.index.total_components,
            'total_ports': self.index.total_ports,
            'total_packages': self.index.total_packages,
            'indexed_words': len(self.index.text_index),
            'search_history_size': len(self.search_history)
        }
    
    def clear_history(self):
        """Clear search history"""
        self.search_history.clear()