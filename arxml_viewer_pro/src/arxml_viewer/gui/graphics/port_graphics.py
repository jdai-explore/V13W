# src/arxml_viewer/gui/graphics/port_graphics.py
"""
Enhanced Port Graphics Item - Day 4 Implementation
Provides advanced port interactions, selection, and context menus
"""

from typing import Optional, List, Dict, Any, Callable
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QMenu, QAction, 
    QGraphicsSceneContextMenuEvent, QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent, QApplication, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QObject, QTimer
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QCursor

from ...models.port import Port, PortType
from ...models.interface import Interface, InterfaceType
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class PortGraphicsItem(QGraphicsEllipseItem):
    """
    Enhanced port graphics item with advanced interactions
    Supports selection, context menus, hover effects, and connection preview
    """
    
    def __init__(self, port: Port, parent_component=None):
        super().__init__(parent_component)
        
        self.logger = get_logger(__name__)
        self.port = port
        self.parent_component = parent_component
        
        # State management
        self.is_highlighted = False
        self.is_selected_port = False
        self.is_hovering = False
        self.is_connection_preview = False
        
        # Visual properties
        self.normal_size = UIConstants.COMPONENT_PORT_SIZE
        self.hover_size = self.normal_size * 1.3
        self.selected_size = self.normal_size * 1.5
        
        # Connection preview
        self.compatible_ports: List['PortGraphicsItem'] = []
        self.preview_connections: List[QGraphicsItem] = []
        
        # Setup port
        self._setup_port()
        self._setup_interactions()
        
        # Error handling
        try:
            self._validate_port_data()
        except Exception as e:
            self.logger.error(f"Port validation failed: {e}")
            self._set_error_state()
    
    def _setup_port(self):
        """Setup port visual properties"""
        try:
            # Set port size
            size = self.normal_size
            self.setRect(0, 0, size, size)
            
            # Set port appearance based on type
            self._update_port_appearance()
            
            # Set tooltip
            self.setToolTip(self._generate_enhanced_tooltip())
            
            # Enable interactions
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
            self.setAcceptHoverEvents(True)
            
            # Set z-value to appear above component
            self.setZValue(10)
            
        except Exception as e:
            self.logger.error(f"Port setup failed: {e}")
            self._set_error_state()
    
    def _setup_interactions(self):
        """Setup port interaction handlers"""
        try:
            # Context menu policy
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            
            # Hover effects timer
            self.hover_timer = QTimer()
            self.hover_timer.setSingleShot(True)
            self.hover_timer.timeout.connect(self._on_hover_timeout)
            
        except Exception as e:
            self.logger.error(f"Interaction setup failed: {e}")
    
    def _validate_port_data(self):
        """Validate port data integrity"""
        if not self.port:
            raise ValueError("Port data is None")
        
        if not self.port.short_name:
            raise ValueError("Port missing short_name")
        
        if not isinstance(self.port.port_type, PortType):
            raise ValueError(f"Invalid port type: {self.port.port_type}")
    
    def _set_error_state(self):
        """Set port to error state with visual indication"""
        try:
            self.setBrush(QBrush(QColor(255, 0, 0, 100)))  # Red with transparency
            self.setPen(QPen(QColor(255, 0, 0), 2))
            self.setToolTip("⚠️ Port Error - Invalid port data")
        except Exception:
            pass  # Fail silently for error state
    
    def _update_port_appearance(self):
        """Update port appearance based on type and state"""
        try:
            # Get base color for port type
            if self.port.is_provided:
                base_color = QColor(*AppConstants.PORT_COLORS['PROVIDED'])
            elif self.port.is_required:
                base_color = QColor(*AppConstants.PORT_COLORS['REQUIRED'])
            else:
                base_color = QColor(*AppConstants.PORT_COLORS['PROVIDED_REQUIRED'])
            
            # Adjust color based on state
            if self.is_selected_port:
                # Bright outline for selection
                self.setPen(QPen(QColor(255, 255, 0), 3))
                self.setBrush(QBrush(base_color))
            elif self.is_highlighted:
                # Enhanced color for highlighting
                enhanced_color = base_color.lighter(130)
                self.setPen(QPen(enhanced_color.darker(150), 2))
                self.setBrush(QBrush(enhanced_color))
            elif self.is_hovering:
                # Subtle highlight for hover
                hover_color = base_color.lighter(120)
                self.setPen(QPen(hover_color.darker(130), 2))
                self.setBrush(QBrush(hover_color))
            else:
                # Normal appearance
                self.setPen(QPen(base_color.darker(150), 1))
                self.setBrush(QBrush(base_color))
            
            # Update size based on state
            current_size = self.normal_size
            if self.is_selected_port:
                current_size = self.selected_size
            elif self.is_hovering:
                current_size = self.hover_size
            
            # Animate size change
            current_rect = self.rect()
            center = current_rect.center()
            new_rect = QRectF(0, 0, current_size, current_size)
            new_rect.moveCenter(center)
            self.setRect(new_rect)
            
        except Exception as e:
            self.logger.error(f"Appearance update failed: {e}")
    
    def _generate_enhanced_tooltip(self) -> str:
        """Generate comprehensive tooltip with interface information"""
        try:
            tooltip_parts = [f"<b>🔌 {self.port.short_name}</b>"]
            
            # Port type with icon
            port_icon = "🟢" if self.port.is_provided else "🔴"
            tooltip_parts.append(f"{port_icon} Type: {self.port.port_type.value}")
            
            # Interface information
            if self.port.interface_ref:
                tooltip_parts.append(f"📋 Interface: {self.port.interface_ref}")
            
            # Enhanced interface details if available
            if hasattr(self.port, 'interface') and self.port.interface:
                interface = self.port.interface
                tooltip_parts.append(f"🔧 Interface Type: {interface.interface_type.value}")
                
                if interface.methods:
                    tooltip_parts.append(f"📝 Methods: {len(interface.methods)}")
                
                if interface.data_elements:
                    tooltip_parts.append(f"📊 Data Elements: {len(interface.data_elements)}")
            
            # Component information
            if self.parent_component and hasattr(self.parent_component, 'component'):
                comp = self.parent_component.component
                tooltip_parts.append(f"⚙️ Component: {comp.short_name}")
            
            # Description
            if self.port.desc:
                desc = self.port.desc
                if len(desc) > 100:
                    desc = desc[:97] + "..."
                tooltip_parts.append(f"📄 {desc}")
            
            # UUID for debugging
            tooltip_parts.append(f"🔑 UUID: {self.port.uuid[:8]}...")
            
            # Connection information
            if hasattr(self, 'connection_count'):
                tooltip_parts.append(f"🔗 Connections: {self.connection_count}")
            
            return "<br>".join(tooltip_parts)
            
        except Exception as e:
            self.logger.error(f"Tooltip generation failed: {e}")
            return f"⚠️ Port: {getattr(self.port, 'short_name', 'Unknown')}"
    
    # === Event Handlers ===
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle mouse press for port selection"""
        try:
            if event.button() == Qt.LeftButton:
                self.select_port()
                self.logger.debug(f"Port selected: {self.port.short_name}")
            
            super().mousePressEvent(event)
            
        except Exception as e:
            self.logger.error(f"Mouse press handling failed: {e}")
    
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle double-click to show port details"""
        try:
            if event.button() == Qt.LeftButton:
                self.show_port_details()
                
        except Exception as e:
            self.logger.error(f"Double-click handling failed: {e}")
    
    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent):
        """Show context menu for port"""
        try:
            menu = self._create_context_menu()
            if menu:
                menu.exec_(event.screenPos())
                
        except Exception as e:
            self.logger.error(f"Context menu failed: {e}")
    
    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        """Handle hover enter"""
        try:
            self.is_hovering = True
            self._update_port_appearance()
            
            # Start connection preview after delay
            self.hover_timer.start(500)  # 500ms delay
            
            # Update cursor
            self.setCursor(QCursor(Qt.PointingHandCursor))
            
            super().hoverEnterEvent(event)
            
        except Exception as e:
            self.logger.error(f"Hover enter failed: {e}")
    
    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        """Handle hover leave"""
        try:
            self.is_hovering = False
            self._update_port_appearance()
            
            # Cancel connection preview
            self.hover_timer.stop()
            self._clear_connection_preview()
            
            # Reset cursor
            self.setCursor(QCursor(Qt.ArrowCursor))
            
            super().hoverLeaveEvent(event)
            
        except Exception as e:
            self.logger.error(f"Hover leave failed: {e}")
    
    def _on_hover_timeout(self):
        """Handle hover timeout for connection preview"""
        try:
            if self.is_hovering:
                self._show_connection_preview()
        except Exception as e:
            self.logger.error(f"Hover timeout failed: {e}")
    
    # === Public Interface ===
    
    def select_port(self):
        """Select this port"""
        try:
            # Clear other port selections in scene
            if self.scene():
                for item in self.scene().items():
                    if isinstance(item, PortGraphicsItem) and item != self:
                        item.deselect_port()
            
            self.is_selected_port = True
            self._update_port_appearance()
            
            # Emit selection signal if parent component has it
            if (self.parent_component and 
                hasattr(self.parent_component, 'port_selected')):
                self.parent_component.port_selected.emit(self.port)
            
        except Exception as e:
            self.logger.error(f"Port selection failed: {e}")
    
    def deselect_port(self):
        """Deselect this port"""
        try:
            self.is_selected_port = False
            self._update_port_appearance()
        except Exception as e:
            self.logger.error(f"Port deselection failed: {e}")
    
    def highlight_port(self, highlight_type: str = "selection"):
        """Highlight port with specific type"""
        try:
            self.is_highlighted = True
            self._update_port_appearance()
            
            self.logger.debug(f"Port highlighted: {self.port.short_name} ({highlight_type})")
            
        except Exception as e:
            self.logger.error(f"Port highlighting failed: {e}")
    
    def clear_highlight(self):
        """Clear port highlighting"""
        try:
            self.is_highlighted = False
            self._update_port_appearance()
        except Exception as e:
            self.logger.error(f"Clear highlight failed: {e}")
    
    def show_port_details(self):
        """Show detailed port information dialog"""
        try:
            from ..dialogs.port_details_dialog import PortDetailsDialog
            
            dialog = PortDetailsDialog(self.port, parent=None)
            dialog.exec_()
            
        except ImportError:
            # Fallback to simple message box
            self._show_simple_port_details()
        except Exception as e:
            self.logger.error(f"Port details dialog failed: {e}")
            self._show_simple_port_details()
    
    def _show_simple_port_details(self):
        """Show simple port details in message box"""
        try:
            details = f"""Port Details

Name: {self.port.short_name}
Type: {self.port.port_type.value}
UUID: {self.port.uuid}

Interface: {self.port.interface_ref or 'None'}

Description:
{self.port.desc or 'No description available'}
"""
            
            QMessageBox.information(None, "Port Details", details)
            
        except Exception as e:
            self.logger.error(f"Simple port details failed: {e}")
    
    def _create_context_menu(self) -> Optional[QMenu]:
        """Create context menu for port"""
        try:
            menu = QMenu()
            
            # Port details action
            details_action = QAction("📋 Port Details...", None)
            details_action.triggered.connect(self.show_port_details)
            menu.addAction(details_action)
            
            menu.addSeparator()
            
            # Interface actions
            if self.port.interface_ref:
                interface_action = QAction(f"🔧 Show Interface: {self.port.interface_ref}", None)
                interface_action.triggered.connect(self._show_interface_details)
                menu.addAction(interface_action)
            
            # Connection actions
            find_connections_action = QAction("🔗 Find Connections", None)
            find_connections_action.triggered.connect(self._find_port_connections)
            menu.addAction(find_connections_action)
            
            menu.addSeparator()
            
            # Copy actions
            copy_name_action = QAction("📋 Copy Name", None)
            copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(self.port.short_name))
            menu.addAction(copy_name_action)
            
            copy_uuid_action = QAction("🔑 Copy UUID", None)
            copy_uuid_action.triggered.connect(lambda: self._copy_to_clipboard(self.port.uuid))
            menu.addAction(copy_uuid_action)
            
            return menu
            
        except Exception as e:
            self.logger.error(f"Context menu creation failed: {e}")
            return None
    
    def _show_interface_details(self):
        """Show interface details"""
        try:
            # This would open interface details dialog
            QMessageBox.information(None, "Interface Details", 
                                  f"Interface: {self.port.interface_ref}\n\n"
                                  "Interface details would be shown here.")
        except Exception as e:
            self.logger.error(f"Interface details failed: {e}")
    
    def _find_port_connections(self):
        """Find and highlight port connections"""
        try:
            # This would find and highlight connections
            QMessageBox.information(None, "Port Connections", 
                                  f"Connections for port '{self.port.short_name}' would be highlighted.")
        except Exception as e:
            self.logger.error(f"Find connections failed: {e}")
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except Exception as e:
            self.logger.error(f"Clipboard copy failed: {e}")
    
    # === Connection Preview ===
    
    def _show_connection_preview(self):
        """Show connection preview for compatible ports"""
        try:
            if not self.scene():
                return
            
            # Find compatible ports
            compatible_ports = self._find_compatible_ports()
            
            if compatible_ports:
                self._highlight_compatible_ports(compatible_ports)
                self.logger.debug(f"Showing connection preview for {len(compatible_ports)} compatible ports")
            
        except Exception as e:
            self.logger.error(f"Connection preview failed: {e}")
    
    def _find_compatible_ports(self) -> List['PortGraphicsItem']:
        """Find ports that can connect to this port"""
        try:
            compatible = []
            
            if not self.scene():
                return compatible
            
            # Get all port items in scene
            for item in self.scene().items():
                if isinstance(item, PortGraphicsItem) and item != self:
                    if self._are_ports_compatible(self.port, item.port):
                        compatible.append(item)
            
            return compatible
            
        except Exception as e:
            self.logger.error(f"Finding compatible ports failed: {e}")
            return []
    
    def _are_ports_compatible(self, port1: Port, port2: Port) -> bool:
        """Check if two ports are compatible for connection"""
        try:
            # Basic compatibility rules:
            # 1. Provided port can connect to Required port
            # 2. Same interface (if specified)
            # 3. Different components
            
            # Check port types
            if port1.is_provided and port2.is_required:
                compatible = True
            elif port1.is_required and port2.is_provided:
                compatible = True
            else:
                compatible = False
            
            # Check interfaces match (if both have interfaces)
            if (compatible and port1.interface_ref and port2.interface_ref):
                compatible = port1.interface_ref == port2.interface_ref
            
            # Check different components
            if compatible and port1.component_uuid and port2.component_uuid:
                compatible = port1.component_uuid != port2.component_uuid
            
            return compatible
            
        except Exception as e:
            self.logger.error(f"Port compatibility check failed: {e}")
            return False
    
    def _highlight_compatible_ports(self, compatible_ports: List['PortGraphicsItem']):
        """Highlight compatible ports"""
        try:
            for port_item in compatible_ports:
                port_item.is_connection_preview = True
                port_item._update_port_appearance()
                
                # Draw connection line preview
                self._draw_connection_preview(port_item)
            
        except Exception as e:
            self.logger.error(f"Highlighting compatible ports failed: {e}")
    
    def _draw_connection_preview(self, target_port: 'PortGraphicsItem'):
        """Draw preview connection line to target port"""
        try:
            if not self.scene():
                return
            
            # Simple line from this port to target port
            from PyQt5.QtWidgets import QGraphicsLineItem
            
            start_pos = self.scenePos() + self.rect().center()
            end_pos = target_port.scenePos() + target_port.rect().center()
            
            line_item = QGraphicsLineItem(start_pos.x(), start_pos.y(), 
                                        end_pos.x(), end_pos.y())
            
            # Style the preview line
            pen = QPen(QColor(255, 255, 0, 128), 2)  # Semi-transparent yellow
            pen.setStyle(Qt.DashLine)
            line_item.setPen(pen)
            line_item.setZValue(5)  # Below ports but above components
            
            self.scene().addItem(line_item)
            self.preview_connections.append(line_item)
            
        except Exception as e:
            self.logger.error(f"Drawing connection preview failed: {e}")
    
    def _clear_connection_preview(self):
        """Clear all connection preview visuals"""
        try:
            # Clear preview lines
            if self.scene():
                for line_item in self.preview_connections:
                    if line_item.scene():
                        self.scene().removeItem(line_item)
            
            self.preview_connections.clear()
            
            # Clear port highlighting
            if self.scene():
                for item in self.scene().items():
                    if isinstance(item, PortGraphicsItem):
                        if item.is_connection_preview:
                            item.is_connection_preview = False
                            item._update_port_appearance()
            
        except Exception as e:
            self.logger.error(f"Clearing connection preview failed: {e}")
    
    # === Utility Methods ===
    
    def get_port_center_scene_pos(self) -> QPointF:
        """Get center position of port in scene coordinates"""
        try:
            return self.scenePos() + self.rect().center()
        except Exception as e:
            self.logger.error(f"Getting port center failed: {e}")
            return QPointF(0, 0)
    
    def set_connection_count(self, count: int):
        """Set number of connections for this port"""
        try:
            self.connection_count = count
            self.setToolTip(self._generate_enhanced_tooltip())
        except Exception as e:
            self.logger.error(f"Setting connection count failed: {e}")
    
    def __str__(self) -> str:
        """String representation"""
        try:
            return f"PortGraphicsItem({self.port.short_name}, {self.port.port_type.value})"
        except Exception:
            return "PortGraphicsItem(Invalid)"