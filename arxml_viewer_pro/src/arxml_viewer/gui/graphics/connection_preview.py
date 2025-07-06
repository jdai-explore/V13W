# src/arxml_viewer/gui/graphics/connection_preview.py
"""
Connection Preview System - Day 4 Implementation
Complete implementation for visual connection preview, validation, and compatibility checking
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from PyQt5.QtWidgets import (
    QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPathItem,
    QGraphicsItem, QGraphicsScene, QGraphicsTextItem
)
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import (
    QColor, QPen, QBrush, QPainterPath, QLinearGradient, 
    QFont, QPainter, QPolygonF
)

from ...models.port import Port, PortType
from ...models.component import Component
from ...utils.constants import AppConstants, UIConstants
from ...utils.logger import get_logger

class ConnectionCompatibility:
    """Connection compatibility analyzer"""
    
    @staticmethod
    def are_ports_compatible(port1: Port, port2: Port) -> Tuple[bool, str]:
        """
        Check if two ports are compatible for connection
        
        Returns:
            Tuple of (is_compatible, reason)
        """
        try:
            # Rule 1: Different port types required
            if port1.port_type == port2.port_type:
                if port1.port_type == PortType.PROVIDED_REQUIRED:
                    # P/R ports can connect to each other
                    pass
                else:
                    return False, "Cannot connect ports of same type"
            
            # Rule 2: Must have compatible directions
            if not ConnectionCompatibility._check_port_directions(port1, port2):
                return False, "Incompatible port directions"
            
            # Rule 3: Interface compatibility
            compatible, reason = ConnectionCompatibility._check_interface_compatibility(port1, port2)
            if not compatible:
                return False, reason
            
            # Rule 4: Different components
            if port1.component_uuid and port2.component_uuid:
                if port1.component_uuid == port2.component_uuid:
                    return False, "Cannot connect ports within same component"
            
            return True, "Ports are compatible"
            
        except Exception as e:
            return False, f"Compatibility check failed: {e}"
    
    @staticmethod
    def _check_port_directions(port1: Port, port2: Port) -> bool:
        """Check if port directions are compatible"""
        # Provided can connect to Required
        if port1.is_provided and port2.is_required:
            return True
        if port1.is_required and port2.is_provided:
            return True
        
        # P/R ports are flexible
        if (port1.port_type == PortType.PROVIDED_REQUIRED or 
            port2.port_type == PortType.PROVIDED_REQUIRED):
            return True
        
        return False
    
    @staticmethod
    def _check_interface_compatibility(port1: Port, port2: Port) -> Tuple[bool, str]:
        """Check interface compatibility"""
        # If both have interface references, they must match
        interface_ref1 = getattr(port1, 'interface_ref', None)
        interface_ref2 = getattr(port2, 'interface_ref', None)
        
        if interface_ref1 and interface_ref2:
            if interface_ref1 == interface_ref2:
                return True, "Interfaces match"
            else:
                return False, f"Interface mismatch: {interface_ref1} vs {interface_ref2}"
        
        # If one has interface and other doesn't, it's potentially compatible
        if interface_ref1 or interface_ref2:
            return True, "Partial interface compatibility"
        
        # If neither has interface, assume compatible
        return True, "No interface constraints"

class ConnectionPreviewLine(QGraphicsLineItem):
    """
    Enhanced connection preview line with styling and animation
    """
    
    def __init__(self, start_port, end_port, compatibility_score: float = 1.0):
        super().__init__()
        
        self.start_port = start_port
        self.end_port = end_port
        self.compatibility_score = compatibility_score
        
        # Visual properties
        self.line_width = 2
        self.z_value = 5
        
        # Animation
        self.animation_phase = 0.0
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate)
        
        # Setup line
        self._setup_line()
        self._start_animation()
    
    def _setup_line(self):
        """Setup line appearance based on compatibility"""
        try:
            # Calculate line endpoints
            start_pos = self._get_port_position(self.start_port)
            end_pos = self._get_port_position(self.end_port)
            
            if start_pos and end_pos:
                self.setLine(start_pos.x(), start_pos.y(), end_pos.x(), end_pos.y())
            
            # Style based on compatibility score
            if self.compatibility_score >= 0.8:
                # High compatibility - green
                color = QColor(76, 175, 80, 180)
            elif self.compatibility_score >= 0.5:
                # Medium compatibility - yellow
                color = QColor(255, 193, 7, 180)
            else:
                # Low compatibility - red
                color = QColor(244, 67, 54, 180)
            
            pen = QPen(color, self.line_width)
            pen.setStyle(Qt.DashLine)
            self.setPen(pen)
            
            # Set z-value
            self.setZValue(self.z_value)
            
        except Exception as e:
            # Fallback to simple line
            pen = QPen(QColor(128, 128, 128, 128), 2)
            pen.setStyle(Qt.DashLine)
            self.setPen(pen)
    
    def _get_port_position(self, port_item) -> Optional[QPointF]:
        """Get port position in scene coordinates"""
        try:
            if hasattr(port_item, 'get_port_center_scene_pos'):
                return port_item.get_port_center_scene_pos()
            elif hasattr(port_item, 'scenePos') and hasattr(port_item, 'rect'):
                return port_item.scenePos() + port_item.rect().center()
            else:
                return QPointF(0, 0)
        except Exception:
            return QPointF(0, 0)
    
    def _start_animation(self):
        """Start line animation"""
        try:
            self.animation_timer.start(100)  # 100ms intervals
        except Exception:
            pass  # Animation is optional
    
    def _animate(self):
        """Animate the line (dash offset)"""
        try:
            self.animation_phase += 0.2
            if self.animation_phase >= 1.0:
                self.animation_phase = 0.0
            
            # Update pen dash pattern
            pen = self.pen()
            dash_pattern = [4, 4]  # 4 pixels on, 4 pixels off
            pen.setDashPattern(dash_pattern)
            pen.setDashOffset(self.animation_phase * 8)
            self.setPen(pen)
            
        except Exception:
            pass  # Animation errors are not critical
    
    def stop_animation(self):
        """Stop line animation"""
        try:
            if self.animation_timer.isActive():
                self.animation_timer.stop()
        except Exception:
            pass

class ConnectionArrow(QGraphicsPathItem):
    """Arrow head for connection preview"""
    
    def __init__(self, start_point: QPointF, end_point: QPointF, color: QColor):
        super().__init__()
        
        self.start_point = start_point
        self.end_point = end_point
        self.color = color
        
        self._create_arrow_path()
        self._setup_appearance()
    
    def _create_arrow_path(self):
        """Create arrow head path"""
        try:
            import math
            
            # Calculate arrow direction
            dx = self.end_point.x() - self.start_point.x()
            dy = self.end_point.y() - self.start_point.y()
            
            if dx == 0 and dy == 0:
                return
            
            # Arrow dimensions
            arrow_length = 12
            
            # Calculate angle
            angle = math.atan2(dy, dx)
            
            # Arrow points
            tip = self.end_point
            
            # Back points
            back_angle1 = angle + math.pi - 0.5
            back_angle2 = angle + math.pi + 0.5
            
            back1 = QPointF(
                tip.x() + arrow_length * math.cos(back_angle1),
                tip.y() + arrow_length * math.sin(back_angle1)
            )
            
            back2 = QPointF(
                tip.x() + arrow_length * math.cos(back_angle2),
                tip.y() + arrow_length * math.sin(back_angle2)
            )
            
            # Create path
            path = QPainterPath()
            path.moveTo(tip)
            path.lineTo(back1)
            path.lineTo(back2)
            path.lineTo(tip)
            
            self.setPath(path)
            
        except Exception:
            # Create simple triangle if calculation fails
            path = QPainterPath()
            path.addEllipse(self.end_point.x() - 3, self.end_point.y() - 3, 6, 6)
            self.setPath(path)
    
    def _setup_appearance(self):
        """Setup arrow appearance"""
        try:
            self.setBrush(QBrush(self.color))
            self.setPen(QPen(self.color.darker(120), 1))
            self.setZValue(6)
        except Exception:
            pass

class ConnectionPreviewManager(QObject):
    """
    Manages connection preview system for the graphics scene
    Complete implementation for Day 4
    """
    
    # Signals
    connection_preview_started = pyqtSignal(object)  # source_port
    connection_preview_ended = pyqtSignal()
    compatibility_checked = pyqtSignal(object, object, bool, str)  # port1, port2, compatible, reason
    
    def __init__(self, graphics_scene):
        super().__init__()
        
        self.logger = get_logger(__name__)
        self.graphics_scene = graphics_scene
        
        # Preview state
        self.active_preview_port = None
        self.preview_items: List[QGraphicsItem] = []
        self.compatible_ports: Dict[str, Tuple[object, float]] = {}
        
        # Timers
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self._show_preview)
        
        self.cleanup_timer = QTimer()
        self.cleanup_timer.setSingleShot(True)
        self.cleanup_timer.timeout.connect(self._cleanup_preview)
        
        # Settings
        self.preview_delay_ms = 500
        self.preview_duration_ms = 5000
        self.max_preview_connections = 10
    
    def start_connection_preview(self, source_port):
        """Start connection preview from source port"""
        try:
            if hasattr(source_port, 'port'):
                port_name = source_port.port.short_name
            else:
                port_name = "Unknown"
            
            self.logger.debug(f"Starting connection preview for port: {port_name}")
            
            # Clear any existing preview
            self.clear_preview()
            
            # Set active port
            self.active_preview_port = source_port
            
            # Start preview timer
            self.preview_timer.start(self.preview_delay_ms)
            
            # Emit signal
            self.connection_preview_started.emit(source_port)
            
        except Exception as e:
            self.logger.error(f"Failed to start connection preview: {e}")
    
    def _show_preview(self):
        """Show connection preview after delay"""
        try:
            if not self.active_preview_port:
                return
            
            # Find compatible ports
            compatible_ports = self._find_compatible_ports()
            
            if not compatible_ports:
                self.logger.debug("No compatible ports found")
                return
            
            # Create preview visuals
            self._create_preview_visuals(compatible_ports)
            
            # Start cleanup timer
            self.cleanup_timer.start(self.preview_duration_ms)
            
            self.logger.debug(f"Showing preview for {len(compatible_ports)} compatible ports")
            
        except Exception as e:
            self.logger.error(f"Failed to show preview: {e}")
    
    def _find_compatible_ports(self) -> List[Tuple[object, float]]:
        """Find ports compatible with source port"""
        try:
            compatible = []
            
            if not self.graphics_scene or not self.active_preview_port:
                return compatible
            
            source_port = getattr(self.active_preview_port, 'port', None)
            if not source_port:
                return compatible
            
            # Get all component items in scene
            components = getattr(self.graphics_scene, 'components', {})
            
            for comp_uuid, comp_item in components.items():
                # Skip same component
                if hasattr(comp_item, 'component') and comp_item.component.uuid == source_port.component_uuid:
                    continue
                
                # Check enhanced port items first
                port_items = getattr(comp_item, 'enhanced_port_items', [])
                if not port_items:
                    # Fallback to regular port items
                    port_items = getattr(comp_item, 'port_items', [])
                
                for port_item in port_items:
                    try:
                        target_port = getattr(port_item, 'port', None)
                        if not target_port:
                            continue
                        
                        # Check compatibility
                        is_compatible, reason = ConnectionCompatibility.are_ports_compatible(
                            source_port, target_port
                        )
                        
                        if is_compatible:
                            # Calculate compatibility score
                            score = self._calculate_compatibility_score(source_port, target_port)
                            compatible.append((port_item, score))
                            
                            # Emit compatibility signal
                            self.compatibility_checked.emit(
                                source_port, target_port, True, reason
                            )
                        else:
                            # Emit incompatibility signal for debugging
                            self.compatibility_checked.emit(
                                source_port, target_port, False, reason
                            )
                            
                    except Exception as e:
                        self.logger.warning(f"Compatibility check failed for port: {e}")
                        continue
                
                # Limit number of previews
                if len(compatible) >= self.max_preview_connections:
                    break
            
            # Sort by compatibility score (highest first)
            compatible.sort(key=lambda x: x[1], reverse=True)
            
            return compatible[:self.max_preview_connections]
            
        except Exception as e:
            self.logger.error(f"Finding compatible ports failed: {e}")
            return []
    
    def _calculate_compatibility_score(self, port1: Port, port2: Port) -> float:
        """Calculate compatibility score between ports"""
        try:
            score = 1.0
            
            # Interface match bonus
            interface_ref1 = getattr(port1, 'interface_ref', None)
            interface_ref2 = getattr(port2, 'interface_ref', None)
            
            if interface_ref1 and interface_ref2:
                if interface_ref1 == interface_ref2:
                    score += 0.5  # Perfect match
                else:
                    score -= 0.3  # Interface mismatch penalty
            elif interface_ref1 or interface_ref2:
                score -= 0.1  # Partial interface penalty
            
            # Port type compatibility
            if ((port1.is_provided and port2.is_required) or 
                (port1.is_required and port2.is_provided)):
                score += 0.2  # Perfect direction match
            
            # Ensure score is in valid range
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Compatibility score calculation failed: {e}")
            return 0.5  # Default medium score
    
    def _create_preview_visuals(self, compatible_ports: List[Tuple[object, float]]):
        """Create visual preview elements"""
        try:
            if not self.active_preview_port or not self.graphics_scene:
                return
            
            for port_item, compatibility_score in compatible_ports:
                # Create preview line
                preview_line = ConnectionPreviewLine(
                    self.active_preview_port, port_item, compatibility_score
                )
                self.graphics_scene.addItem(preview_line)
                self.preview_items.append(preview_line)
                
                # Get positions for arrow
                start_pos = self._get_port_position(self.active_preview_port)
                end_pos = self._get_port_position(port_item)
                
                if start_pos and end_pos:
                    # Create arrow
                    if compatibility_score >= 0.8:
                        color = QColor(76, 175, 80, 200)
                    elif compatibility_score >= 0.5:
                        color = QColor(255, 193, 7, 200)
                    else:
                        color = QColor(244, 67, 54, 200)
                    
                    arrow = ConnectionArrow(start_pos, end_pos, color)
                    self.graphics_scene.addItem(arrow)
                    self.preview_items.append(arrow)
                
                # Highlight compatible port
                if hasattr(port_item, 'highlight_port'):
                    port_item.highlight_port("connection_preview")
                
                # Create compatibility info label
                info_label = self._create_compatibility_label(
                    port_item, compatibility_score
                )
                if info_label:
                    self.graphics_scene.addItem(info_label)
                    self.preview_items.append(info_label)
            
            # Highlight source port
            if hasattr(self.active_preview_port, 'highlight_port'):
                self.active_preview_port.highlight_port("connection_source")
            
        except Exception as e:
            self.logger.error(f"Creating preview visuals failed: {e}")
    
    def _get_port_position(self, port_item) -> Optional[QPointF]:
        """Get port position in scene coordinates"""
        try:
            if hasattr(port_item, 'get_port_center_scene_pos'):
                return port_item.get_port_center_scene_pos()
            elif hasattr(port_item, 'scenePos') and hasattr(port_item, 'rect'):
                return port_item.scenePos() + port_item.rect().center()
            else:
                return None
        except Exception as e:
            self.logger.error(f"Getting port position failed: {e}")
            return None
    
    def _create_compatibility_label(self, port_item, score: float) -> Optional[QGraphicsTextItem]:
        """Create compatibility info label"""
        try:
            # Create text item
            label = QGraphicsTextItem()
            
            # Format score
            percentage = int(score * 100)
            score_text = f"{percentage}%"
            
            # Set text and font
            label.setPlainText(score_text)
            font = QFont("Arial", 8, QFont.Bold)
            label.setFont(font)
            
            # Position near port
            port_pos = self._get_port_position(port_item)
            if port_pos:
                label.setPos(port_pos.x() + 15, port_pos.y() - 10)
            
            # Color based on score
            if score >= 0.8:
                color = QColor(76, 175, 80)
            elif score >= 0.5:
                color = QColor(255, 193, 7)
            else:
                color = QColor(244, 67, 54)
            
            label.setDefaultTextColor(color)
            label.setZValue(7)
            
            return label
            
        except Exception as e:
            self.logger.error(f"Creating compatibility label failed: {e}")
            return None
    
    def clear_preview(self):
        """Clear all preview visuals"""
        try:
            # Stop timers
            self.preview_timer.stop()
            self.cleanup_timer.stop()
            
            # Remove preview items from scene
            if self.graphics_scene:
                for item in self.preview_items:
                    if item.scene():
                        self.graphics_scene.removeItem(item)
                    
                    # Stop animation if it's a preview line
                    if isinstance(item, ConnectionPreviewLine):
                        item.stop_animation()
            
            self.preview_items.clear()
            
            # Clear port highlighting
            self._clear_all_port_highlighting()
            
            # Reset state
            self.active_preview_port = None
            self.compatible_ports.clear()
            
            # Emit signal
            self.connection_preview_ended.emit()
            
        except Exception as e:
            self.logger.error(f"Clearing preview failed: {e}")
    
    def _clear_all_port_highlighting(self):
        """Clear all port highlighting in scene"""
        try:
            if not self.graphics_scene:
                return
            
            components = getattr(self.graphics_scene, 'components', {})
            
            for comp_item in components.values():
                # Clear enhanced port highlighting
                port_items = getattr(comp_item, 'enhanced_port_items', [])
                if not port_items:
                    # Fallback to regular port items
                    port_items = getattr(comp_item, 'port_items', [])
                
                for port_item in port_items:
                    if hasattr(port_item, 'clear_highlight'):
                        port_item.clear_highlight()
            
        except Exception as e:
            self.logger.error(f"Clearing port highlighting failed: {e}")
    
    def _cleanup_preview(self):
        """Auto-cleanup preview after timeout"""
        try:
            self.clear_preview()
            self.logger.debug("Preview auto-cleanup completed")
        except Exception as e:
            self.logger.error(f"Preview cleanup failed: {e}")
    
    def is_preview_active(self) -> bool:
        """Check if preview is currently active"""
        return self.active_preview_port is not None
    
    def get_preview_statistics(self) -> Dict[str, Any]:
        """Get preview system statistics"""
        try:
            source_port_name = None
            if self.active_preview_port and hasattr(self.active_preview_port, 'port'):
                source_port_name = self.active_preview_port.port.short_name
            
            return {
                'active_preview': self.is_preview_active(),
                'preview_items_count': len(self.preview_items),
                'compatible_ports_count': len(self.compatible_ports),
                'source_port': source_port_name
            }
        except Exception as e:
            self.logger.error(f"Getting preview statistics failed: {e}")
            return {}
    
    def set_preview_settings(self, delay_ms: int = None, duration_ms: int = None, max_connections: int = None):
        """Update preview settings"""
        try:
            if delay_ms is not None:
                self.preview_delay_ms = max(100, delay_ms)
            
            if duration_ms is not None:
                self.preview_duration_ms = max(1000, duration_ms)
            
            if max_connections is not None:
                self.max_preview_connections = max(1, min(20, max_connections))
                
            self.logger.debug(f"Preview settings updated: delay={self.preview_delay_ms}ms, "
                            f"duration={self.preview_duration_ms}ms, max={self.max_preview_connections}")
            
        except Exception as e:
            self.logger.error(f"Setting preview settings failed: {e}")

class ConnectionValidator:
    """
    Advanced connection validation with business rules
    """
    
    @staticmethod
    def validate_connection_rules(port1: Port, port2: Port, components: Dict[str, Component] = None) -> Tuple[bool, List[str]]:
        """
        Validate connection against advanced business rules
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        try:
            # Basic compatibility check
            is_compatible, reason = ConnectionCompatibility.are_ports_compatible(port1, port2)
            if not is_compatible:
                issues.append(f"Basic compatibility: {reason}")
            
            # Additional validation rules can be added here
            # For Day 4, we keep it simple
            
            return len(issues) == 0, issues
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
            return False, issues