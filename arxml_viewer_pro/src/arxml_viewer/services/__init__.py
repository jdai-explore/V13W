# src/arxml_viewer/services/__init__.py
"""
Services Module - Search, Filter, and other service components
"""

# Try to import services with fallback handling
try:
    from .search_engine import SearchEngine, SearchScope, SearchMode, SearchResult
    SEARCH_ENGINE_AVAILABLE = True
    print("✅ Search engine loaded")
except ImportError as e:
    print(f"⚠️ Search engine not available: {e}")
    SEARCH_ENGINE_AVAILABLE = False
    
    # Create fallback classes
    class SearchEngine:
        def __init__(self):
            self.indexed_items = []
        
        def build_index(self, packages):
            pass
        
        def search(self, query, scope=None, mode=None, max_results=50):
            return []
        
        def get_search_suggestions(self, query, max_suggestions=10):
            return []
    
    class SearchScope:
        ALL = "all"
        COMPONENTS = "components"
        PORTS = "ports"
        PACKAGES = "packages"
    
    class SearchMode:
        CONTAINS = "contains"
        STARTS_WITH = "starts_with"
        ENDS_WITH = "ends_with"
        EXACT = "exact"
        REGEX = "regex"
        FUZZY = "fuzzy"
    
    class SearchResult:
        def __init__(self, item_name="", item_type="", item_uuid="", match_field="", relevance_score=0.0):
            self.item_name = item_name
            self.item_type = item_type
            self.item_uuid = item_uuid
            self.match_field = match_field
            self.relevance_score = relevance_score
            self.parent_package = None
            self.match_text = None

try:
    from .filter_manager import FilterManager
    FILTER_MANAGER_AVAILABLE = True
    print("✅ Filter manager loaded")
except ImportError as e:
    print(f"⚠️ Filter manager not available: {e}")
    FILTER_MANAGER_AVAILABLE = False
    
    # Create fallback class
    class FilterManager:
        def __init__(self):
            self.active_filters = {}
        
        def apply_quick_filter(self, filter_type):
            self.active_filters['quick'] = filter_type
        
        def filter_components(self, components):
            return components
        
        def clear_filters(self):
            self.active_filters.clear()

__all__ = [
    'SearchEngine', 'SearchScope', 'SearchMode', 'SearchResult',
    'FilterManager',
    'SEARCH_ENGINE_AVAILABLE', 'FILTER_MANAGER_AVAILABLE'
]

print(f"🔧 Services module initialized - Search: {SEARCH_ENGINE_AVAILABLE}, Filter: {FILTER_MANAGER_AVAILABLE}")