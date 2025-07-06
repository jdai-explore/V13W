# src/arxml_viewer/gui/dialogs/port_details_dialog.py
"""
Port Details Dialog - Day 4 Implementation
Comprehensive port information display with interface details
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit, 
    QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QScrollArea, QWidget,
    QHeaderView, QAbstractItemView, QSplitter, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QIcon

from ...models.port import Port, PortType
from ...models.interface import Interface, InterfaceType
from ...utils.constants import AppConstants
from ...utils.logger import get_logger

class PortDetailsDialog(QDialog):
    """
    Comprehensive port details dialog with tabbed interface
    Shows port properties, interface information, and connection details
    """
    
    # Signals
    port_modified = pyqtSignal(object)  # Port object
    interface_requested = pyqtSignal(str)  # Interface reference
    connection_requested = pyqtSignal(str)  # Port UUID
    
    def __init__(self, port: Port, parent=None):
        super().__init__(parent)
        
        self.logger = get_logger(__name__)
        self.port = port
        
        # Dialog properties
        self.setWindowTitle(f"Port Details - {port.short_name}")
        self.setModal(True)
        self.resize(800, 600)
        
        # Setup UI
        try:
            self._setup_ui()
            self._populate_data()
            self._setup_connections()
        except Exception as e:
            self.logger.error(f"Port details dialog setup failed: {e}")
            self._show_error_message(f"Failed to initialize dialog: {e}")
    
    def _setup_ui(self):
        """Setup dialog UI with tabbed interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Header with port icon and name
        header = self._create_header()
        layout.addWidget(header)
        
        # Main content with tabs
        self.tab_widget = QTabWidget()
        
        # Tab 1: Basic Properties
        self.properties_tab = self._create_properties_tab()
        self.tab_widget.addTab(self.properties_tab, "🔧 Properties")
        
        # Tab 2: Interface Information
        self.interface_tab = self._create_interface_tab()
        self.tab_widget.addTab(self.interface_tab, "📋 Interface")
        
        # Tab 3: Connections
        self.connections_tab = self._create_connections_tab()
        self.tab_widget.addTab(self.connections_tab, "🔗 Connections")
        
        # Tab 4: Advanced/Debug
        self.debug_tab = self._create_debug_tab()
        self.tab_widget.addTab(self.debug_tab, "🔍 Debug")
        
        layout.addWidget(self.tab_widget)
        
        # Button bar
        button_layout = self._create_button_bar()
        layout.addLayout(button_layout)
        
        # Apply styling
        self._apply_styling()
    
    def _create_header(self) -> QWidget:
        """Create dialog header with port information"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_layout = QHBoxLayout(header_frame)
        
        # Port icon/type indicator
        port_icon = QLabel()
        if self.port.is_provided:
            port_icon.setText("🟢")
            port_icon.setToolTip("Provided Port")
        elif self.port.is_required:
            port_icon.setText("🔴")
            port_icon.setToolTip("Required Port")
        else:
            port_icon.setText("🟡")
            port_icon.setToolTip("Provided/Required Port")
        
        port_icon.setFont(QFont("Arial", 24))
        header_layout.addWidget(port_icon)
        
        # Port name and basic info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.port.short_name or "Unnamed Port")
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        info_layout.addWidget(name_label)
        
        type_label = QLabel(f"Type: {self.port.port_type.value}")
        type_label.setFont(QFont("Arial", 10))
        info_layout.addWidget(type_label)
        
        if self.port.interface_ref:
            interface_label = QLabel(f"Interface: {self.port.interface_ref}")
            interface_label.setFont(QFont("Arial", 10))
            info_layout.addWidget(interface_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        return header_frame
    
    def _create_properties_tab(self) -> QWidget:
        """Create properties tab with port details"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Basic properties group
        basic_group = QGroupBox("Basic Properties")
        basic_layout = QFormLayout(basic_group)
        
        # Create read-only fields
        self.name_field = QLineEdit(self.port.short_name or "")
        self.name_field.setReadOnly(True)
        basic_layout.addRow("Name:", self.name_field)
        
        self.type_field = QLineEdit(self.port.port_type.value)
        self.type_field.setReadOnly(True)
        basic_layout.addRow("Type:", self.type_field)
        
        self.uuid_field = QLineEdit(self.port.uuid)
        self.uuid_field.setReadOnly(True)
        basic_layout.addRow("UUID:", self.uuid_field)
        
        if self.port.component_uuid:
            self.component_field = QLineEdit(self.port.component_uuid)
            self.component_field.setReadOnly(True)
            basic_layout.addRow("Component:", self.component_field)
        
        layout.addWidget(basic_group)
        
        # Description group
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)
        
        self.description_text = QTextEdit()
        self.description_text.setPlainText(self.port.desc or "No description available")
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(100)
        desc_layout.addWidget(self.description_text)
        
        layout.addWidget(desc_group)
        
        # Properties summary
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        summary_text = self._generate_properties_summary()
        summary_label = QLabel(summary_text)
        summary_label.setWordWrap(True)
        summary_layout.addWidget(summary_label)
        
        layout.addWidget(summary_group)
        
        layout.addStretch()
        return tab
    
    def _create_interface_tab(self) -> QWidget:
        """Create interface tab with detailed interface information"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        if not self.port.interface_ref:
            # No interface message
            no_interface_label = QLabel("This port does not reference an interface")
            no_interface_label.setAlignment(Qt.AlignCenter)
            no_interface_label.setStyleSheet("color: #666; font-style: italic; font-size: 14px;")
            layout.addWidget(no_interface_label)
        else:
            # Interface reference group
            ref_group = QGroupBox("Interface Reference")
            ref_layout = QFormLayout(ref_group)
            
            self.interface_ref_field = QLineEdit(self.port.interface_ref)
            self.interface_ref_field.setReadOnly(True)
            ref_layout.addRow("Reference:", self.interface_ref_field)
            
            # Button to show full interface details
            interface_btn = QPushButton("📋 View Interface Details")
            interface_btn.clicked.connect(self._show_interface_details)
            ref_layout.addRow("", interface_btn)
            
            layout.addWidget(ref_group)
            
            # Interface details (if available)
            if hasattr(self.port, 'interface') and self.port.interface:
                interface_details = self._create_interface_details_widget()
                layout.addWidget(interface_details)
            else:
                # Interface not loaded
                loading_label = QLabel("Interface details not loaded")
                loading_label.setStyleSheet("color: #888; font-style: italic;")
                layout.addWidget(loading_label)
        
        layout.addStretch()
        return tab
    
    def _create_interface_details_widget(self) -> QWidget:
        """Create widget showing detailed interface information"""
        group = QGroupBox("Interface Details")
        layout = QVBoxLayout(group)
        
        interface = self.port.interface
        
        # Interface type
        type_layout = QFormLayout()
        type_field = QLineEdit(interface.interface_type.value)
        type_field.setReadOnly(True)
        type_layout.addRow("Type:", type_field)
        layout.addLayout(type_layout)
        
        # Methods table
        if interface.methods:
            methods_label = QLabel(f"Methods ({len(interface.methods)}):")
            methods_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(methods_label)
            
            methods_table = QTableWidget()
            methods_table.setColumnCount(3)
            methods_table.setHorizontalHeaderLabels(["Name", "Type", "Description"])
            methods_table.setRowCount(len(interface.methods))
            
            for i, method in enumerate(interface.methods):
                methods_table.setItem(i, 0, QTableWidgetItem(method.get('name', 'Unknown')))
                methods_table.setItem(i, 1, QTableWidgetItem(method.get('type', 'Unknown')))
                methods_table.setItem(i, 2, QTableWidgetItem(method.get('description', '')))
            
            methods_table.resizeColumnsToContents()
            methods_table.setMaximumHeight(150)
            layout.addWidget(methods_table)
        
        # Data elements table
        if interface.data_elements:
            data_label = QLabel(f"Data Elements ({len(interface.data_elements)}):")
            data_label.setFont(QFont("Arial", 10, QFont.Bold))
            layout.addWidget(data_label)
            
            data_table = QTableWidget()
            data_table.setColumnCount(3)
            data_table.setHorizontalHeaderLabels(["Name", "Type", "Description"])
            data_table.setRowCount(len(interface.data_elements))
            
            for i, element in enumerate(interface.data_elements):
                data_table.setItem(i, 0, QTableWidgetItem(element.get('name', 'Unknown')))
                data_table.setItem(i, 1, QTableWidgetItem(element.get('type', 'Unknown')))
                data_table.setItem(i, 2, QTableWidgetItem(element.get('description', '')))
            
            data_table.resizeColumnsToContents()
            data_table.setMaximumHeight(150)
            layout.addWidget(data_table)
        
        return group
    
    def _create_connections_tab(self) -> QWidget:
        """Create connections tab showing port connections"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Connections summary
        summary_group = QGroupBox("Connection Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        # This would be populated with actual connection data
        self.connections_count_label = QLabel("Connections: Not available")
        summary_layout.addWidget(self.connections_count_label)
        
        layout.addWidget(summary_group)
        
        # Connections table
        connections_group = QGroupBox("Connected Ports")
        connections_layout = QVBoxLayout(connections_group)
        
        self.connections_table = QTableWidget()
        self.connections_table.setColumnCount(4)
        self.connections_table.setHorizontalHeaderLabels([
            "Connected Port", "Component", "Connection Type", "Interface"
        ])
        
        # Set table properties
        self.connections_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.connections_table.setAlternatingRowColors(True)
        self.connections_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        connections_layout.addWidget(self.connections_table)
        
        # Buttons for connection actions
        conn_buttons = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Connections")
        refresh_btn.clicked.connect(self._refresh_connections)
        conn_buttons.addWidget(refresh_btn)
        
        find_btn = QPushButton("🔍 Find in Diagram")
        find_btn.clicked.connect(self._find_connections_in_diagram)
        conn_buttons.addWidget(find_btn)
        
        conn_buttons.addStretch()
        connections_layout.addLayout(conn_buttons)
        
        layout.addWidget(connections_group)
        
        layout.addStretch()
        return tab
    
    def _create_debug_tab(self) -> QWidget:
        """Create debug tab with technical information"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Raw data group
        raw_group = QGroupBox("Raw Port Data")
        raw_layout = QVBoxLayout(raw_group)
        
        self.raw_data_text = QTextEdit()
        self.raw_data_text.setReadOnly(True)
        self.raw_data_text.setFont(QFont("Courier", 9))
        raw_layout.addWidget(self.raw_data_text)
        
        layout.addWidget(raw_group)
        
        # Actions group
        actions_group = QGroupBox("Debug Actions")
        actions_layout = QHBoxLayout(actions_group)
        
        copy_uuid_btn = QPushButton("📋 Copy UUID")
        copy_uuid_btn.clicked.connect(lambda: self._copy_to_clipboard(self.port.uuid))
        actions_layout.addWidget(copy_uuid_btn)
        
        copy_data_btn = QPushButton("📋 Copy Raw Data")
        copy_data_btn.clicked.connect(self._copy_raw_data)
        actions_layout.addWidget(copy_data_btn)
        
        validate_btn = QPushButton("✅ Validate Port")
        validate_btn.clicked.connect(self._validate_port)
        actions_layout.addWidget(validate_btn)
        
        actions_layout.addStretch()
        layout.addWidget(actions_group)
        
        return tab
    
    def _create_button_bar(self) -> QHBoxLayout:
        """Create dialog button bar"""
        button_layout = QHBoxLayout()
        
        # Action buttons
        self.edit_btn = QPushButton("✏️ Edit Port")
        self.edit_btn.clicked.connect(self._edit_port)
        self.edit_btn.setEnabled(False)  # Disabled for now
        button_layout.addWidget(self.edit_btn)
        
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.clicked.connect(self._export_port_data)
        button_layout.addWidget(self.export_btn)
        
        button_layout.addStretch()
        
        # Standard buttons
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        return button_layout
    
    def _setup_connections(self):
        """Setup signal connections"""
        try:
            # Auto-refresh timer
            self.refresh_timer = QTimer()
            self.refresh_timer.timeout.connect(self._auto_refresh)
            self.refresh_timer.start(5000)  # Refresh every 5 seconds
            
        except Exception as e:
            self.logger.error(f"Setup connections failed: {e}")
    
    def _apply_styling(self):
        """Apply custom styling to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cccccc;
                border-radius: 5px;
                margin: 5px 0;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLineEdit[readOnly="true"] {
                background-color: #f9f9f9;
                color: #333333;
                border: 1px solid #dddddd;
            }
            QTextEdit[readOnly="true"] {
                background-color: #f9f9f9;
                color: #333333;
                border: 1px solid #dddddd;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                border-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #bbdefb;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #f5f5f5;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 2px solid #1976d2;
            }
        """)
    
    def _populate_data(self):
        """Populate dialog with port data"""
        try:
            # Populate raw data tab
            raw_data = self._generate_raw_data()
            self.raw_data_text.setPlainText(raw_data)
            
            # Populate connections if available
            self._populate_connections()
            
        except Exception as e:
            self.logger.error(f"Data population failed: {e}")
    
    def _generate_properties_summary(self) -> str:
        """Generate properties summary text"""
        try:
            summary_parts = []
            
            # Port characteristics
            if self.port.is_provided:
                summary_parts.append("• This port provides interfaces to other components")
            elif self.port.is_required:
                summary_parts.append("• This port requires interfaces from other components")
            else:
                summary_parts.append("• This port both provides and requires interfaces")
            
            # Interface information
            if self.port.interface_ref:
                summary_parts.append(f"• Uses interface: {self.port.interface_ref}")
            else:
                summary_parts.append("• No interface reference specified")
            
            # Component information
            if self.port.component_uuid:
                summary_parts.append(f"• Belongs to component: {self.port.component_uuid[:8]}...")
            
            return "\n".join(summary_parts)
            
        except Exception as e:
            self.logger.error(f"Properties summary generation failed: {e}")
            return "Summary generation failed"
    
    def _generate_raw_data(self) -> str:
        """Generate raw port data for debug tab"""
        try:
            import json
            
            # Convert port to dictionary
            port_dict = {
                'uuid': self.port.uuid,
                'short_name': self.port.short_name,
                'desc': self.port.desc,
                'port_type': self.port.port_type.value,
                'interface_ref': self.port.interface_ref,
                'component_uuid': self.port.component_uuid,
                'position': getattr(self.port, 'position', None),
                'is_provided': self.port.is_provided,
                'is_required': self.port.is_required
            }
            
            # Add interface data if available
            if hasattr(self.port, 'interface') and self.port.interface:
                port_dict['interface'] = {
                    'interface_type': self.port.interface.interface_type.value,
                    'methods': self.port.interface.methods,
                    'data_elements': self.port.interface.data_elements
                }
            
            return json.dumps(port_dict, indent=2)
            
        except Exception as e:
            self.logger.error(f"Raw data generation failed: {e}")
            return f"Raw data generation failed: {e}"
    
    def _populate_connections(self):
        """Populate connections table"""
        try:
            # This would be populated with actual connection data from the scene
            # For now, show placeholder
            self.connections_count_label.setText("Connections: 0 (Feature in development)")
            
            # Clear existing rows
            self.connections_table.setRowCount(0)
            
            # Add placeholder row
            self.connections_table.setRowCount(1)
            self.connections_table.setItem(0, 0, QTableWidgetItem("No connections found"))
            self.connections_table.setItem(0, 1, QTableWidgetItem("-"))
            self.connections_table.setItem(0, 2, QTableWidgetItem("-"))
            self.connections_table.setItem(0, 3, QTableWidgetItem("-"))
            
        except Exception as e:
            self.logger.error(f"Connections population failed: {e}")
    
    # === Event Handlers ===
    
    def _show_interface_details(self):
        """Show detailed interface information"""
        try:
            self.interface_requested.emit(self.port.interface_ref)
        except Exception as e:
            self.logger.error(f"Show interface details failed: {e}")
    
    def _refresh_connections(self):
        """Refresh connection information"""
        try:
            self._populate_connections()
            self.logger.debug("Connections refreshed")
        except Exception as e:
            self.logger.error(f"Refresh connections failed: {e}")
    
    def _find_connections_in_diagram(self):
        """Find and highlight connections in main diagram"""
        try:
            self.connection_requested.emit(self.port.uuid)
        except Exception as e:
            self.logger.error(f"Find connections failed: {e}")
    
    def _edit_port(self):
        """Edit port properties"""
        try:
            # Would open port editing dialog
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, "Edit Port", 
                                  "Port editing functionality will be available in a future version.")
        except Exception as e:
            self.logger.error(f"Edit port failed: {e}")
    
    def _export_port_data(self):
        """Export port data to file"""
        try:
            from PyQt5.QtWidgets import QFileDialog, QMessageBox
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Port Data", 
                f"{self.port.short_name}_port_data.json",
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if filename:
                raw_data = self._generate_raw_data()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(raw_data)
                
                QMessageBox.information(self, "Export Successful", 
                                      f"Port data exported to:\n{filename}")
                
        except Exception as e:
            self.logger.error(f"Export failed: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Export Failed", f"Failed to export data:\n{e}")
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            from PyQt5.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except Exception as e:
            self.logger.error(f"Copy to clipboard failed: {e}")
    
    def _copy_raw_data(self):
        """Copy raw data to clipboard"""
        try:
            raw_data = self._generate_raw_data()
            self._copy_to_clipboard(raw_data)
        except Exception as e:
            self.logger.error(f"Copy raw data failed: {e}")
    
    def _validate_port(self):
        """Validate port data integrity"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            
            issues = []
            
            # Check required fields
            if not self.port.short_name:
                issues.append("Missing short_name")
            
            if not self.port.uuid:
                issues.append("Missing UUID")
            
            if not isinstance(self.port.port_type, PortType):
                issues.append("Invalid port_type")
            
            # Check interface reference
            if self.port.interface_ref and not hasattr(self.port, 'interface'):
                issues.append("Interface reference exists but interface not loaded")
            
            if issues:
                QMessageBox.warning(self, "Validation Issues", 
                                  f"Port validation found issues:\n\n" + "\n".join(f"• {issue}" for issue in issues))
            else:
                QMessageBox.information(self, "Validation Successful", 
                                      "Port data validation passed successfully.")
                
        except Exception as e:
            self.logger.error(f"Port validation failed: {e}")
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Validation Error", f"Validation failed:\n{e}")
    
    def _auto_refresh(self):
        """Auto-refresh dialog data"""
        try:
            # Refresh connections data
            if self.tab_widget.currentIndex() == 2:  # Connections tab
                self._populate_connections()
        except Exception as e:
            self.logger.error(f"Auto-refresh failed: {e}")
    
    def _show_error_message(self, message: str):
        """Show error message to user"""
        try:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", message)
        except Exception:
            pass  # Fail silently for error display
    
    def closeEvent(self, event):
        """Handle dialog close event"""
        try:
            # Stop refresh timer
            if hasattr(self, 'refresh_timer'):
                self.refresh_timer.stop()
            
            event.accept()
            
        except Exception as e:
            self.logger.error(f"Close event handling failed: {e}")
            event.accept()