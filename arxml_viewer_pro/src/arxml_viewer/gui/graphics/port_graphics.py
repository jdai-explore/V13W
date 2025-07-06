# src/arxml_viewer/gui/graphics/enhanced_port_graphics.py
"""
Enhanced Port Graphics Item - Day 4 Implementation
Provides advanced port interactions, selection, context menus, and interface display
"""

from typing import Optional, List, Dict, Any, Callable
from PyQt5.QtWidgets import (
    QGraphicsEllipseItem, QGraphicsItem, QMenu, QAction, 
    QGraphicsSceneContextMenuEvent, QGraphicsSceneHoverEvent,
    QGraphicsSceneMouseEvent, QApplication, QMessageBox,
    QGraphicsTextItem, QGraphicsRectItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPointF, QObject, QTimer
from PyQt5.QtGui import QColor, QPen, QBrush, QPainter, QCursor, QFont

from ...models.port import Port, PortType
from ...models.interface import Interface, InterfaceType
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class EnhancedPortGraphicsItem(QGraphicsEllipseItem):
    """
    Enhanced port graphics item with Day 4 advanced interactions
    Supports selection, context menus, hover effects, interface display, and connection preview
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
        self.is_error_state = False
        
        # Visual properties
        self.normal_size = UIConstants.COMPONENT_PORT_SIZE
        self.hover_size = self.normal_size * 1.3
        self.selected_size = self.normal_size * 1.5
        
        # Interface display
        self.interface_label: Optional[QGraphicsTextItem] = None
        self.interface_indicator: Optional[QGraphicsRectItem] = None
        self.show_interface_info = False
        
        # Connection preview
        self.compatible_ports: List['EnhancedPortGraphicsItem'] = []
        self.preview_connections: List[QGraphicsItem] = []
        
        # Animation and effects
        self.hover_timer = QTimer()
        self.hover_timer.setSingleShot(True)
        self.hover_timer.timeout.connect(self._on_hover_timeout)
        
        self.pulse_timer = QTimer()
        self.pulse_timer.timeout.connect(self._pulse_animation)
        self.pulse_phase = 0.0
        
        # Setup port
        self._setup_port()
        self._setup_interactions()
        
        # Error handling and validation
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
            self.setRect(-size/2, -size/2, size, size)
            
            # Set port appearance based on type
            self._update_port_appearance()
            
            # Set enhanced tooltip
            self.setToolTip(self._generate_enhanced_tooltip())
            
            # Enable interactions
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            self.setFlag(QGraphicsItem.ItemIsFocusable, True)
            self.setAcceptHoverEvents(True)
            
            # Set z-value to appear above component
            self.setZValue(10)
            
            # Create interface indicator if port has interface
            self._create_interface_indicator()
            
        except Exception as e:
            self.logger.error(f"Port setup failed: {e}")
            self._set_error_state()
    
    def _setup_interactions(self):
        """Setup port interaction handlers"""
        try:
            # Context menu policy
            self.setFlag(QGraphicsItem.ItemIsSelectable, True)
            
            # Hover effects timer
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
            self.is_error_state = True
            self.setBrush(QBrush(QColor(255, 0, 0, 100)))  # Red with transparency
            self.setPen(QPen(QColor(255, 0, 0), 2))
            self.setToolTip("⚠️ Port Error - Invalid port data")
        except Exception:
            pass  # Fail silently for error state
    
    def _update_port_appearance(self):
        """Update port appearance based on type and state"""
        try:
            if self.is_error_state:
                return  # Don't override error state
            
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
            elif self.is_connection_preview:
                # Special color for connection preview
                preview_color = QColor(255, 215, 0)  # Gold
                self.setPen(QPen(preview_color, 3))
                self.setBrush(QBrush(preview_color.lighter(150)))
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
            
            # Update rect with new size, keeping center position
            center = self.rect().center()
            new_rect = QRectF(-current_size/2, -current_size/2, current_size, current_size)
            self.setRect(new_rect)
            
            # Update interface indicator
            self._update_interface_indicator()
            
        except Exception as e:
            self.logger.error(f"Appearance update failed: {e}")
    
    def _create_interface_indicator(self):
        """Create interface indicator for ports with interfaces"""
        try:
            if not self.port.interface_ref:
                return
            
            # Create small indicator rectangle
            indicator_size = 4
            self.interface_indicator = QGraphicsRectItem(
                self.normal_size/2 - indicator_size/2,
                -self.normal_size/2 - indicator_size,
                indicator_size,
                indicator_size,
                self
            )
            
            # Style the indicator
            self.interface_indicator.setBrush(QBrush(QColor(0, 100, 200)))
            self.interface_indicator.setPen(QPen(QColor(0, 50, 150), 1))
            self.interface_indicator.setZValue(11)
            self.interface_indicator.setToolTip(f"Interface: {self.port.interface_ref}")
            
        except Exception as e:
            self.logger.error(f"Interface indicator creation failed: {e}")
    
    def _update_interface_indicator(self):
        """Update interface indicator position and visibility"""
        try:
            if not self.interface_indicator:
                return
            
            # Update position based on current port size
            current_size = self.rect().width()
            indicator_size = 4
            
            self.interface_indicator.setRect(
                current_size/2 - indicator_size/2,
                -current_size/2 - indicator_size - 2,
                indicator_size,
                indicator_size
            )
            
            # Show/hide based on state
            self.interface_indicator.setVisible(self.is_hovering or self.is_selected_port)
            
        except Exception as e:
            self.logger.error(f"Interface indicator update failed: {e}")
    
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
                    # Show first few method names
                    method_names = [m.name for m in interface.methods[:3]]
                    if len(interface.methods) > 3:
                        method_names.append("...")
                    tooltip_parts.append(f"   • {', '.join(method_names)}")
                
                if interface.data_elements:
                    tooltip_parts.append(f"📊 Data Elements: {len(interface.data_elements)}")
                    # Show first few element names
                    element_names = [e.name for e in interface.data_elements[:3]]
                    if len(interface.data_elements) > 3:
                        element_names.append("...")
                    tooltip_parts.append(f"   • {', '.join(element_names)}")
            
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
            
            # Compatibility info during preview
            if self.is_connection_preview:
                tooltip_parts.append("✨ Compatible for connection")
            
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
                
                # Emit signal to parent component if available
                if self.parent_component and hasattr(self.parent_component, 'port_selected'):
                    self.parent_component.port_selected.emit(self.port)
            
            super().mousePressEvent(event)
            
        except Exception as e:
            self.logger.error(f"Mouse press handling failed: {e}")
    
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent):
        """Handle double-click to show port details"""
        try:
            if event.button() == Qt.LeftButton:
                self.show_port_details()
                
                # Emit signal to parent component if available
                if self.parent_component and hasattr(self.parent_component, 'port_double_clicked'):
                    self.parent_component.port_double_clicked.emit(self.port)
                
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
        """Handle hover enter with enhanced effects"""
        try:
            self.is_hovering = True
            self._update_port_appearance()
            
            # Start connection preview after delay
            self.hover_timer.start(500)  # 500ms delay
            
            # Update cursor
            self.setCursor(QCursor(Qt.PointingHandCursor))
            
            # Start pulse animation for visual feedback
            if not self.pulse_timer.isActive():
                self.pulse_timer.start(100)  # 100ms intervals
            
            super().hoverEnterEvent(event)
            
        except Exception as e:
            self.logger.error(f"Hover enter failed: {e}")
    
    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        """Handle hover leave with cleanup"""
        try:
            self.is_hovering = False
            self._update_port_appearance()
            
            # Cancel connection preview
            self.hover_timer.stop()
            self._clear_connection_preview()
            
            # Stop pulse animation
            self.pulse_timer.stop()
            
            # Reset cursor
            self.setCursor(QCursor(Qt.ArrowCursor))
            
            super().hoverLeaveEvent(event)
            
        except Exception as e:
            self.logger.error(f"Hover leave failed: {e}")
    
    def _on_hover_timeout(self):
        """Handle hover timeout for connection preview"""
        try:
            if self.is_hovering and self.scene():
                # Request connection preview from scene
                scene = self.scene()
                if hasattr(scene, 'connection_preview_manager'):
                    scene.connection_preview_manager.start_connection_preview(self)
        except Exception as e:
            self.logger.error(f"Hover timeout failed: {e}")
    
    def _pulse_animation(self):
        """Pulse animation for visual feedback"""
        try:
            if not self.is_hovering:
                self.pulse_timer.stop()
                return
            
            self.pulse_phase += 0.2
            if self.pulse_phase >= 6.28:  # 2π
                self.pulse_phase = 0.0
            
            # Subtle pulse effect by adjusting opacity
            import math
            pulse_opacity = 0.7 + 0.3 * math.sin(self.pulse_phase)
            self.setOpacity(pulse_opacity)
            
        except Exception:
            pass  # Animation errors are not critical
    
    # === Public Interface Methods ===
    
    def select_port(self):
        """Select this port with enhanced visual feedback"""
        try:
            # Clear other port selections in scene
            if self.scene():
                for item in self.scene().items():
                    if isinstance(item, EnhancedPortGraphicsItem) and item != self:
                        item.deselect_port()
            
            self.is_selected_port = True
            self._update_port_appearance()
            
            # Show interface information
            self._show_interface_info()
            
            self.logger.debug(f"Enhanced port selected: {self.port.short_name}")
            
        except Exception as e:
            self.logger.error(f"Port selection failed: {e}")
    
    def deselect_port(self):
        """Deselect this port"""
        try:
            self.is_selected_port = False
            self._update_port_appearance()
            self._hide_interface_info()
            
        except Exception as e:
            self.logger.error(f"Port deselection failed: {e}")
    
    def highlight_port(self, highlight_type: str = "selection"):
        """Highlight port with specific type and enhanced effects"""
        try:
            self.is_highlighted = True
            
            if highlight_type == "connection_preview":
                self.is_connection_preview = True
            elif highlight_type == "connection_source":
                # Special highlighting for connection source
                self.is_connection_preview = True
                self._start_pulse_animation()
            
            self._update_port_appearance()
            
            self.logger.debug(f"Port highlighted: {self.port.short_name} ({highlight_type})")
            
        except Exception as e:
            self.logger.error(f"Port highlighting failed: {e}")
    
    def clear_highlight(self):
        """Clear port highlighting with cleanup"""
        try:
            self.is_highlighted = False
            self.is_connection_preview = False
            self._stop_pulse_animation()
            self._update_port_appearance()
            
        except Exception as e:
            self.logger.error(f"Clear highlight failed: {e}")
    
    def show_port_details(self):
        """Show detailed port information dialog"""
        try:
            # Try to import and use the enhanced port details dialog
            from ..dialogs.port_details_dialog import PortDetailsDialog
            
            dialog = PortDetailsDialog(self.port, parent=None)
            
            # Connect dialog signals if available
            if hasattr(dialog, 'interface_requested'):
                dialog.interface_requested.connect(self._on_interface_requested)
            if hasattr(dialog, 'connection_requested'):
                dialog.connection_requested.connect(self._on_connection_requested)
            
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
            details_parts = [
                f"Port: {self.port.short_name}",
                f"Type: {self.port.port_type.value}",
                f"UUID: {self.port.uuid}"
            ]
            
            if self.port.interface_ref:
                details_parts.append(f"Interface: {self.port.interface_ref}")
            
            if self.port.desc:
                details_parts.append(f"\nDescription:\n{self.port.desc}")
            
            # Add interface details if available
            if hasattr(self.port, 'interface') and self.port.interface:
                interface = self.port.interface
                details_parts.append(f"\nInterface Details:")
                details_parts.append(f"  Type: {interface.interface_type.value}")
                details_parts.append(f"  Methods: {len(interface.methods)}")
                details_parts.append(f"  Data Elements: {len(interface.data_elements)}")
            
            details = "\n".join(details_parts)
            QMessageBox.information(None, "Port Details", details)
            
        except Exception as e:
            self.logger.error(f"Simple port details failed: {e}")
    
    def _show_interface_info(self):
        """Show interface information overlay"""
        try:
            if not self.port.interface_ref or self.interface_label:
                return
            
            # Create interface label
            self.interface_label = QGraphicsTextItem(self.port.interface_ref, self)
            font = QFont("Arial", 8)
            self.interface_label.setFont(font)
            self.interface_label.setDefaultTextColor(QColor(0, 0, 0))
            
            # Position below port
            label_rect = self.interface_label.boundingRect()
            port_rect = self.rect()
            
            x = port_rect.center().x() - label_rect.width() / 2
            y = port_rect.bottom() + 5
            
            self.interface_label.setPos(x, y)
            self.interface_label.setZValue(12)
            
        except Exception as e:
            self.logger.error(f"Interface info display failed: {e}")
    
    def _hide_interface_info(self):
        """Hide interface information overlay"""
        try:
            if self.interface_label:
                if self.interface_label.scene():
                    self.interface_label.scene().removeItem(self.interface_label)
                self.interface_label = None
        except Exception as e:
            self.logger.error(f"Interface info hiding failed: {e}")
    
    def _start_pulse_animation(self):
        """Start pulse animation"""
        try:
            if not self.pulse_timer.isActive():
                self.pulse_phase = 0.0
                self.pulse_timer.start(50)  # Faster for source indication
        except Exception:
            pass
    
    def _stop_pulse_animation(self):
        """Stop pulse animation"""
        try:
            self.pulse_timer.stop()
            self.setOpacity(1.0)  # Reset opacity
        except Exception:
            pass
    
    def _create_context_menu(self) -> Optional[QMenu]:
        """Create enhanced context menu for port"""
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
                
                if hasattr(self.port, 'interface') and self.port.interface:
                    interface_methods_action = QAction("📝 Interface Methods", None)
                    interface_methods_action.triggered.connect(self._show_interface_methods)
                    menu.addAction(interface_methods_action)
            
            # Connection actions
            find_connections_action = QAction("🔗 Find Connections", None)
            find_connections_action.triggered.connect(self._find_port_connections)
            menu.addAction(find_connections_action)
            
            preview_connections_action = QAction("👀 Preview Compatible Ports", None)
            preview_connections_action.triggered.connect(self._preview_compatible_connections)
            menu.addAction(preview_connections_action)
            
            menu.addSeparator()
            
            # Copy actions
            copy_name_action = QAction("📋 Copy Name", None)
            copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(self.port.short_name))
            menu.addAction(copy_name_action)
            
            copy_uuid_action = QAction("🔑 Copy UUID", None)
            copy_uuid_action.triggered.connect(lambda: self._copy_to_clipboard(self.port.uuid))
            menu.addAction(copy_uuid_action)
            
            if self.port.interface_ref:
                copy_interface_action = QAction("🔧 Copy Interface Reference", None)
                copy_interface_action.triggered.connect(lambda: self._copy_to_clipboard(self.port.interface_ref))
                menu.addAction(copy_interface_action)
            
            return menu
            
        except Exception as e:
            self.logger.error(f"Context menu creation failed: {e}")
            return None
    
    # === Context Menu Action Handlers ===
    
    def _show_interface_details(self):
        """Show interface details"""
        try:
            if not self.port.interface_ref:
                return
            
            if hasattr(self.port, 'interface') and self.port.interface:
                # Show detailed interface information
                interface = self.port.interface
                details = interface.generate_documentation()
                
                # Create a simple text dialog (could be enhanced with rich formatting)
                QMessageBox.information(None, f"Interface: {interface.short_name}", 
                                      f"Interface Details:\n\n{details[:1000]}...")
            else:
                QMessageBox.information(None, "Interface Details", 
                                      f"Interface: {self.port.interface_ref}\n\n"
                                      "Interface details not loaded or available.")
        except Exception as e:
            self.logger.error(f"Interface details failed: {e}")
    
    def _show_interface_methods(self):
        """Show interface methods"""
        try:
            if not hasattr(self.port, 'interface') or not self.port.interface:
                return
            
            interface = self.port.interface
            if not interface.methods:
                QMessageBox.information(None, "Interface Methods", 
                                      f"Interface '{interface.short_name}' has no methods.")
                return
            
            methods_text = f"Methods in {interface.short_name}:\n\n"
            for method in interface.methods:
                methods_text += f"• {method.get_signature()}\n"
                if method.description:
                    methods_text += f"  Description: {method.description}\n"
                methods_text += "\n"
            
            QMessageBox.information(None, "Interface Methods", methods_text)
            
        except Exception as e:
            self.logger.error(f"Interface methods display failed: {e}")
    
    def _find_port_connections(self):
        """Find and highlight port connections"""
        try:
            # This would integrate with connection system
            QMessageBox.information(None, "Port Connections", 
                                  f"Finding connections for port '{self.port.short_name}'...\n\n"
                                  "This feature would highlight connected ports in the diagram.")
        except Exception as e:
            self.logger.error(f"Find connections failed: {e}")
    
    def _preview_compatible_connections(self):
        """Preview compatible connections"""
        try:
            if self.scene() and hasattr(self.scene(), 'connection_preview_manager'):
                self.scene().connection_preview_manager.start_connection_preview(self)
            else:
                QMessageBox.information(None, "Connection Preview", 
                                      f"Showing compatible ports for '{self.port.short_name}'...\n\n"
                                      "Compatible ports would be highlighted in the diagram.")
        except Exception as e:
            self.logger.error(f"Connection preview failed: {e}")
    
    def _copy_to_clipboard(self, text: str):
        """Copy text to clipboard"""
        try:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
        except Exception as e:
            self.logger.error(f"Clipboard copy failed: {e}")
    
    # === Signal Handlers ===
    
    def _on_interface_requested(self, interface_ref: str):
        """Handle interface details request from dialog"""
        try:
            # This could emit a signal to the main application to show interface details
            self.logger.debug(f"Interface requested: {interface_ref}")
        except Exception as e:
            self.logger.error(f"Interface request handling failed: {e}")
    
    def _on_connection_requested(self, port_uuid: str):
        """Handle connection request from dialog"""
        try:
            # This could emit a signal to highlight connections
            self.logger.debug(f"Connection requested for port: {port_uuid}")
        except Exception as e:
            self.logger.error(f"Connection request handling failed: {e}")
    
    # === Connection Preview Support ===
    
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
                    if isinstance(item, EnhancedPortGraphicsItem):
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
    
    def get_port_info(self) -> Dict[str, Any]:
        """Get comprehensive port information"""
        try:
            info = {
                'name': self.port.short_name,
                'type': self.port.port_type.value,
                'uuid': self.port.uuid,
                'interface_ref': self.port.interface_ref,
                'description': self.port.desc,
                'is_provided': self.port.is_provided,
                'is_required': self.port.is_required,
                'component_uuid': self.port.component_uuid,
                'state': {
                    'is_selected': self.is_selected_port,
                    'is_highlighted': self.is_highlighted,
                    'is_hovering': self.is_hovering,
                    'is_preview': self.is_connection_preview
                }
            }
            
            # Add interface information if available
            if hasattr(self.port, 'interface') and self.port.interface:
                interface = self.port.interface
                info['interface'] = {
                    'name': interface.short_name,
                    'type': interface.interface_type.value,
                    'methods': len(interface.methods),
                    'data_elements': len(interface.data_elements),
                    'complexity': interface.get_complexity_score()
                }
            
            return info
        except Exception as e:
            self.logger.error(f"Getting port info failed: {e}")
            return {}
    
    def update_from_model(self, updated_port: Port):
        """Update graphics from updated port model"""
        try:
            self.port = updated_port
            self._validate_port_data()
            self._update_port_appearance()
            self.setToolTip(self._generate_enhanced_tooltip())
            
            # Update interface indicator
            if self.interface_indicator:
                if self.port.interface_ref:
                    self.interface_indicator.setVisible(True)
                    self.interface_indicator.setToolTip(f"Interface: {self.port.interface_ref}")
                else:
                    self.interface_indicator.setVisible(False)
            
        except Exception as e:
            self.logger.error(f"Port model update failed: {e}")
            self._set_error_state()
    
    def cleanup(self):
        """Cleanup resources when port is being destroyed"""
        try:
            # Stop timers
            self.hover_timer.stop()
            self.pulse_timer.stop()
            
            # Clear connection preview
            self._clear_connection_preview()
            
            # Hide interface info
            self._hide_interface_info()
            
            # Clear references
            self.compatible_ports.clear()
            
        except Exception as e:
            self.logger.error(f"Port cleanup failed: {e}")
    
    def __str__(self) -> str:
        """String representation"""
        try:
            return f"EnhancedPortGraphicsItem({self.port.short_name}, {self.port.port_type.value})"
        except Exception:
            return "EnhancedPortGraphicsItem(Invalid)"
    
    def __del__(self):
        """Destructor with cleanup"""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore cleanup errors during destruction