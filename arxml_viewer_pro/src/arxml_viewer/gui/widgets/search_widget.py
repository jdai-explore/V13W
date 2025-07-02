# src/arxml_viewer/gui/widgets/search_widget.py
"""
Search Widget - Advanced search and filtering interface
Provides comprehensive search functionality with auto-complete and filtering
"""

from typing import List, Dict, Optional, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, 
    QComboBox, QLabel, QFrame, QCompleter, QListWidget, QListWidgetItem,
    QCheckBox, QGroupBox, QScrollArea, QSizePolicy, QToolButton,
    QMenu, QAction, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QStringListModel, QThread, pyqtSlot
from PyQt5.QtGui import QIcon, QFont, QKeySequence

from ...services.search_engine import SearchEngine, SearchScope, SearchMode, SearchResult
from ...services.filter_manager import FilterManager
from ...utils.logger import get_logger

class SearchResultsWidget(QListWidget):
    """Widget to display search results"""
    
    result_selected = pyqtSignal(object)  # SearchResult
    result_activated = pyqtSignal(object)  # SearchResult (double-click)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.search_results: List[SearchResult] = []
        
        # Setup widget
        self.setAlternatingRowColors(True)
        self.setSelectionMode(QListWidget.SingleSelection)
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to results widget"""
        self.setStyleSheet("""
            QListWidget {
                background-color: #454545;
                color: white;
                border: 1px solid #666;
                border-radius: 3px;
                selection-background-color: #4a90e2;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555;
            }
            QListWidget::item:hover {
                background-color: #4a4a4a;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
            }
        """)
    
    def set_results(self, results: List[SearchResult]):
        """Set search results to display"""
        self.search_results = results
        self.clear()
        
        for result in results:
            self._add_result_item(result)
        
        # Show result count
        if results:
            self.logger.debug(f"Displaying {len(results)} search results")
    
    def _add_result_item(self, result: SearchResult):
        """Add a search result item to the list"""
        # Create display text
        item_text = f"{result.item_name} ({result.item_type})"
        
        if result.parent_package:
            item_text += f" - {result.parent_package}"
        
        # Create list item
        item = QListWidgetItem(item_text)
        item.setData(Qt.UserRole, result)
        
        # Set icon based on item type
        self._set_result_icon(item, result)
        
        # Set tooltip
        tooltip = self._create_result_tooltip(result)
        item.setToolTip(tooltip)
        
        self.addItem(item)
    
    def _set_result_icon(self, item: QListWidgetItem, result: SearchResult):
        """Set icon for result item based on type"""
        # Use text indicators for now (can be replaced with actual icons)
        if result.item_type == 'component':
            item.setText(f"🔧 {item.text()}")
        elif result.item_type == 'port':
            item.setText(f"🔌 {item.text()}")
        elif result.item_type == 'package':
            item.setText(f"📁 {item.text()}")
    
    def _create_result_tooltip(self, result: SearchResult) -> str:
        """Create tooltip for search result"""
        tooltip_parts = [
            f"<b>{result.item_name}</b>",
            f"Type: {result.item_type}",
            f"Match: {result.match_field}",
            f"Relevance: {result.relevance_score:.2f}"
        ]
        
        if result.parent_package:
            tooltip_parts.append(f"Package: {result.parent_package}")
        
        if result.match_text:
            # Truncate long match text
            match_text = result.match_text
            if len(match_text) > 100:
                match_text = match_text[:97] + "..."
            tooltip_parts.append(f"Text: {match_text}")
        
        return "<br>".join(tooltip_parts)
    
    def _on_selection_changed(self):
        """Handle selection change"""
        current_item = self.currentItem()
        if current_item:
            result = current_item.data(Qt.UserRole)
            if result:
                self.result_selected.emit(result)
    
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle item double click"""
        result = item.data(Qt.UserRole)
        if result:
            self.result_activated.emit(result)
    
    def clear_results(self):
        """Clear all results"""
        self.search_results.clear()
        self.clear()

class SearchOptionsWidget(QWidget):
    """Widget for search options and filters"""
    
    options_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup search options UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Search scope group
        scope_group = QGroupBox("Search Scope")
        scope_layout = QVBoxLayout(scope_group)
        
        self.scope_group = QButtonGroup()
        
        # Scope radio buttons
        self.scope_all = QRadioButton("All Items")
        self.scope_all.setChecked(True)
        self.scope_components = QRadioButton("Components Only")
        self.scope_ports = QRadioButton("Ports Only")
        self.scope_packages = QRadioButton("Packages Only")
        
        for radio in [self.scope_all, self.scope_components, self.scope_ports, self.scope_packages]:
            self.scope_group.addButton(radio)
            scope_layout.addWidget(radio)
            radio.toggled.connect(self.options_changed.emit)
        
        layout.addWidget(scope_group)
        
        # Search mode group
        mode_group = QGroupBox("Search Mode")
        mode_layout = QVBoxLayout(mode_group)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Contains",
            "Starts With", 
            "Ends With",
            "Exact Match",
            "Regular Expression",
            "Fuzzy Search"
        ])
        self.mode_combo.currentTextChanged.connect(self.options_changed.emit)
        mode_layout.addWidget(self.mode_combo)
        
        layout.addWidget(mode_group)
        
        # Max results
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        results_row = QHBoxLayout()
        results_row.addWidget(QLabel("Max Results:"))
        
        self.max_results_combo = QComboBox()
        self.max_results_combo.addItems(["10", "25", "50", "100", "All"])
        self.max_results_combo.setCurrentText("50")
        self.max_results_combo.currentTextChanged.connect(self.options_changed.emit)
        results_row.addWidget(self.max_results_combo)
        
        results_layout.addLayout(results_row)
        layout.addWidget(results_group)
        
        layout.addStretch()
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply styling to options widget"""
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #666;
                border-radius: 3px;
                margin: 5px 0;
                padding-top: 10px;
                color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QRadioButton {
                color: white;
                spacing: 5px;
            }
            QRadioButton::indicator {
                width: 13px;
                height: 13px;
            }
            QComboBox {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 2px 4px;
                color: white;
            }
            QLabel {
                color: white;
            }
        """)
    
    def get_search_scope(self) -> SearchScope:
        """Get selected search scope"""
        if self.scope_all.isChecked():
            return SearchScope.ALL
        elif self.scope_components.isChecked():
            return SearchScope.COMPONENTS
        elif self.scope_ports.isChecked():
            return SearchScope.PORTS
        elif self.scope_packages.isChecked():
            return SearchScope.PACKAGES
        return SearchScope.ALL
    
    def get_search_mode(self) -> SearchMode:
        """Get selected search mode"""
        mode_text = self.mode_combo.currentText()
        mode_map = {
            "Contains": SearchMode.CONTAINS,
            "Starts With": SearchMode.STARTS_WITH,
            "Ends With": SearchMode.ENDS_WITH,
            "Exact Match": SearchMode.EXACT,
            "Regular Expression": SearchMode.REGEX,
            "Fuzzy Search": SearchMode.FUZZY
        }
        return mode_map.get(mode_text, SearchMode.CONTAINS)
    
    def get_max_results(self) -> int:
        """Get maximum number of results"""
        max_text = self.max_results_combo.currentText()
        if max_text == "All":
            return 0  # 0 means no limit
        try:
            return int(max_text)
        except ValueError:
            return 50

class AdvancedSearchWidget(QWidget):
    """
    Main advanced search widget combining search input, options, and results
    Provides comprehensive search functionality for ARXML components
    """
    
    # Signals
    search_started = pyqtSignal(str)
    search_completed = pyqtSignal(list)  # List[SearchResult]
    result_selected = pyqtSignal(object)  # SearchResult
    result_activated = pyqtSignal(object)  # SearchResult
    
    def __init__(self, search_engine: SearchEngine = None, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.search_engine = search_engine or SearchEngine()
        
        # Search state
        self.current_results: List[SearchResult] = []
        self.search_history: List[str] = []
        
        # Setup UI
        self._setup_ui()
        self._setup_completer()
        
        # Search timer for delayed search
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
    
    def _setup_ui(self):
        """Setup main search widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Search input section
        search_section = self._create_search_input_section()
        layout.addWidget(search_section)
        
        # Main content area
        content_layout = QHBoxLayout()
        
        # Left side: Search options
        self.options_widget = SearchOptionsWidget()
        self.options_widget.options_changed.connect(self._on_options_changed)
        self.options_widget.setMaximumWidth(200)
        content_layout.addWidget(self.options_widget)
        
        # Right side: Search results
        results_frame = QFrame()
        results_layout = QVBoxLayout(results_frame)
        results_layout.setContentsMargins(0, 0, 0, 0)
        
        # Results header
        results_header = QHBoxLayout()
        self.results_label = QLabel("Search Results")
        self.results_label.setFont(QFont("Arial", 10, QFont.Bold))
        results_header.addWidget(self.results_label)
        
        results_header.addStretch()
        
        # Clear results button
        self.clear_results_btn = QPushButton("Clear")
        self.clear_results_btn.setMaximumWidth(60)
        self.clear_results_btn.clicked.connect(self._clear_results)
        results_header.addWidget(self.clear_results_btn)
        
        results_layout.addLayout(results_header)
        
        # Results list
        self.results_widget = SearchResultsWidget()
        self.results_widget.result_selected.connect(self.result_selected.emit)
        self.results_widget.result_activated.connect(self.result_activated.emit)
        results_layout.addWidget(self.results_widget)
        
        content_layout.addWidget(results_frame, 1)  # Give more space to results
        
        layout.addLayout(content_layout)
        
        # Apply overall styling
        self._apply_styling()
    
    def _create_search_input_section(self) -> QWidget:
        """Create search input section"""
        section = QFrame()
        layout = QVBoxLayout(section)
        layout.setContentsMargins(0, 0, 0, 5)
        
        # Main search row
        search_row = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search components, ports, packages...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.search_input.returnPressed.connect(self._on_search_submitted)
        search_row.addWidget(self.search_input)
        
        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._on_search_submitted)
        self.search_btn.setMaximumWidth(80)
        search_row.addWidget(self.search_btn)
        
        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setMaximumWidth(30)
        self.clear_btn.setToolTip("Clear search")
        self.clear_btn.clicked.connect(self._clear_search)
        search_row.addWidget(self.clear_btn)
        
        layout.addLayout(search_row)
        
        # Quick search buttons row
        quick_row = QHBoxLayout()
        quick_row.addWidget(QLabel("Quick:"))
        
        # Quick search buttons
        quick_buttons = [
            ("Components", "component"),
            ("Ports", "port"), 
            ("Packages", "package")
        ]
        
        for text, search_type in quick_buttons:
            btn = QPushButton(text)
            btn.setMaximumWidth(80)
            btn.clicked.connect(lambda checked, st=search_type: self._quick_search(st))
            quick_row.addWidget(btn)
        
        quick_row.addStretch()
        layout.addLayout(quick_row)
        
        return section
    
    def _setup_completer(self):
        """Setup auto-complete for search input"""
        self.completer = QCompleter()
        self.completer_model = QStringListModel()
        self.completer.setModel(self.completer_model)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.search_input.setCompleter(self.completer)
    
    def _apply_styling(self):
        """Apply styling to search widget"""
        self.setStyleSheet("""
            AdvancedSearchWidget {
                background-color: #404040;
                border: 1px solid #555;
                border-radius: 5px;
            }
            QLineEdit {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 6px;
                color: white;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
            QPushButton {
                background-color: #4a4a4a;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
            QLabel {
                color: white;
            }
            QFrame {
                border: none;
            }
        """)
    
    def _on_search_text_changed(self, text: str):
        """Handle search text change with delay"""
        self.search_timer.stop()
        if text.strip():
            self.search_timer.start(500)  # 500ms delay
        else:
            self._clear_results()
    
    def _on_search_submitted(self):
        """Handle search submission (Enter key or button click)"""
        self.search_timer.stop()
        self._perform_search()
    
    def _on_options_changed(self):
        """Handle search options change"""
        # Re-perform search if we have text
        if self.search_input.text().strip():
            self.search_timer.stop()
            self.search_timer.start(200)  # Shorter delay for options change
    
    def _perform_search(self):
        """Perform the actual search"""
        query = self.search_input.text().strip()
        
        if not query:
            self._clear_results()
            return
        
        self.search_started.emit(query)
        
        # Get search parameters
        scope = self.options_widget.get_search_scope()
        mode = self.options_widget.get_search_mode()
        max_results = self.options_widget.get_max_results()
        
        try:
            # Perform search
            results = self.search_engine.search(
                query=query,
                scope=scope,
                mode=mode,
                max_results=max_results
            )
            
            self.current_results = results
            self.results_widget.set_results(results)
            
            # Update results label
            self.results_label.setText(f"Search Results ({len(results)})")
            
            # Add to search history
            self._add_to_search_history(query)
            
            # Update completer
            self._update_completer()
            
            self.search_completed.emit(results)
            
            self.logger.debug(f"Search completed: '{query}' -> {len(results)} results")
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            self._clear_results()
    
    def _quick_search(self, search_type: str):
        """Perform quick search for specific type"""
        # Set appropriate scope
        if search_type == "component":
            self.options_widget.scope_components.setChecked(True)
        elif search_type == "port":
            self.options_widget.scope_ports.setChecked(True)
        elif search_type == "package":
            self.options_widget.scope_packages.setChecked(True)
        
        # If no search text, search for all items of this type
        if not self.search_input.text().strip():
            self.search_input.setText("*")  # Wildcard search
        
        self._perform_search()
    
    def _clear_search(self):
        """Clear search input and results"""
        self.search_input.clear()
        self._clear_results()
    
    def _clear_results(self):
        """Clear search results"""
        self.current_results.clear()
        self.results_widget.clear_results()
        self.results_label.setText("Search Results")
    
    def _add_to_search_history(self, query: str):
        """Add query to search history"""
        if query in self.search_history:
            self.search_history.remove(query)
        
        self.search_history.insert(0, query)
        
        # Limit history size
        if len(self.search_history) > 20:
            self.search_history = self.search_history[:20]
    
    def _update_completer(self):
        """Update auto-completer with search history and suggestions"""
        suggestions = self.search_history.copy()
        
        # Add search engine suggestions
        current_text = self.search_input.text().strip()
        if current_text:
            engine_suggestions = self.search_engine.get_search_suggestions(current_text, 10)
            suggestions.extend(engine_suggestions)
        
        # Remove duplicates while preserving order
        unique_suggestions = []
        seen = set()
        for suggestion in suggestions:
            if suggestion not in seen:
                unique_suggestions.append(suggestion)
                seen.add(suggestion)
        
        self.completer_model.setStringList(unique_suggestions)
    
    def set_search_engine(self, search_engine: SearchEngine):
        """Set the search engine to use"""
        self.search_engine = search_engine
        self._update_completer()
    
    def get_current_results(self) -> List[SearchResult]:
        """Get current search results"""
        return self.current_results.copy()
    
    def set_search_text(self, text: str):
        """Set search text and perform search"""
        self.search_input.setText(text)
        self._perform_search()
    
    def focus_search_input(self):
        """Focus the search input field"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """Get search statistics"""
        return {
            'current_query': self.search_input.text().strip(),
            'result_count': len(self.current_results),
            'search_scope': self.options_widget.get_search_scope().value,
            'search_mode': self.options_widget.get_search_mode().value,
            'history_size': len(self.search_history)
        }

class CompactSearchWidget(QWidget):
    """Compact search widget for toolbar use"""
    
    search_requested = pyqtSignal(str)
    advanced_search_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup compact search UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Quick search...")
        self.search_input.setMaximumWidth(200)
        self.search_input.returnPressed.connect(self._on_search_submitted)
        layout.addWidget(self.search_input)
        
        # Search button
        self.search_btn = QToolButton()
        self.search_btn.setText("🔍")
        self.search_btn.setToolTip("Search")
        self.search_btn.clicked.connect(self._on_search_submitted)
        layout.addWidget(self.search_btn)
        
        # Advanced search button
        self.advanced_btn = QToolButton()
        self.advanced_btn.setText("⚙️")
        self.advanced_btn.setToolTip("Advanced Search")
        self.advanced_btn.clicked.connect(self.advanced_search_requested.emit)
        layout.addWidget(self.advanced_btn)
        
        # Apply styling
        self._apply_compact_styling()
    
    def _apply_compact_styling(self):
        """Apply styling for compact widget"""
        self.setStyleSheet("""
            QLineEdit {
                background-color: #505050;
                border: 1px solid #666;
                border-radius: 3px;
                padding: 4px;
                color: white;
            }
            QToolButton {
                background-color: #4a4a4a;
                border: 1px solid #666;
                border-radius: 3px;
                color: white;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: #5a5a5a;
            }
        """)
    
    def _on_search_submitted(self):
        """Handle search submission"""
        query = self.search_input.text().strip()
        if query:
            self.search_requested.emit(query)
    
    def set_search_text(self, text: str):
        """Set search text"""
        self.search_input.setText(text)
    
    def clear_search(self):
        """Clear search input"""
        self.search_input.clear()
    
    def focus_search(self):
        """Focus search input"""
        self.search_input.setFocus()
        self.search_input.selectAll()