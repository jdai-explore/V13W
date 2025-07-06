# src/arxml_viewer/utils/layout_algorithms.py
"""
Layout Algorithms - Auto-arrangement of components for ARXML Viewer
Provides intelligent component positioning based on connections and hierarchy
"""

import math
import random
from typing import List, Dict, Tuple, Set, Optional, Any
from dataclasses import dataclass
from enum import Enum

from ..models.component import Component, ComponentType
from ..models.connection import Connection
from ..models.port import Port
from ..utils.constants import AppConstants, UIConstants
from ..utils.logger import get_logger

@dataclass
class ComponentPosition:
    """Represents a component's position and size"""
    x: float
    y: float
    width: float = UIConstants.COMPONENT_MIN_WIDTH
    height: float = UIConstants.COMPONENT_MIN_HEIGHT
    
    @property
    def center_x(self) -> float:
        return self.x + self.width / 2
    
    @property
    def center_y(self) -> float:
        return self.y + self.height / 2
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        return self.y + self.height

class LayoutType(Enum):
    """Available layout algorithms"""
    GRID = "grid"
    HIERARCHICAL = "hierarchical"
    FORCE_DIRECTED = "force_directed"
    CIRCULAR = "circular"
    LAYERED = "layered"

class LayoutParameters:
    """Parameters for layout algorithms"""
    
    def __init__(self):
        # Spacing parameters
        self.component_spacing_x = 180
        self.component_spacing_y = 150
        self.layer_spacing = 200
        self.min_spacing = 100
        
        # Grid parameters
        self.grid_columns = None  # Auto-calculate if None
        
        # Force-directed parameters
        self.repulsion_force = 1000
        self.attraction_force = 0.5
        self.iterations = 50
        self.damping = 0.9
        
        # Hierarchical parameters
        self.hierarchy_direction = "top_down"  # "top_down", "left_right"
        self.group_related = True
        
        # Circular parameters
        self.circle_radius = 300
        self.center_important = True

class GridLayout:
    """Simple grid layout algorithm"""
    
    def __init__(self, parameters: LayoutParameters):
        self.params = parameters
        self.logger = get_logger(__name__)
    
    def apply_layout(self, components: List[Component], 
                    connections: List[Connection] = None) -> Dict[str, ComponentPosition]:
        """Apply grid layout to components"""
        try:
            if not components:
                return {}
            
            positions = {}
            
            # Calculate grid dimensions
            num_components = len(components)
            if self.params.grid_columns:
                cols = self.params.grid_columns
            else:
                # Auto-calculate columns (roughly square grid)
                cols = max(1, math.ceil(math.sqrt(num_components)))
            
            rows = math.ceil(num_components / cols)
            
            # Sort components for better layout
            sorted_components = self._sort_components_for_grid(components)
            
            # Position components in grid
            for i, component in enumerate(sorted_components):
                row = i // cols
                col = i % cols
                
                x = col * self.params.component_spacing_x
                y = row * self.params.component_spacing_y
                
                positions[component.uuid] = ComponentPosition(x, y)
            
            self.logger.info(f"Applied grid layout: {cols}x{rows} for {num_components} components")
            return positions
            
        except Exception as e:
            self.logger.error(f"Grid layout failed: {e}")
            return self._fallback_layout(components)
    
    def _sort_components_for_grid(self, components: List[Component]) -> List[Component]:
        """Sort components for better grid arrangement"""
        # Sort by: 1) Type priority, 2) Port count, 3) Name
        type_priority = {
            ComponentType.COMPOSITION: 0,
            ComponentType.SERVICE: 1,
            ComponentType.APPLICATION: 2,
            ComponentType.SENSOR_ACTUATOR: 3,
            ComponentType.COMPLEX_DEVICE_DRIVER: 4
        }
        
        return sorted(components, key=lambda c: (
            type_priority.get(c.component_type, 5),
            -c.port_count,  # More ports first
            c.short_name or ""
        ))
    
    def _fallback_layout(self, components: List[Component]) -> Dict[str, ComponentPosition]:
        """Simple fallback layout"""
        positions = {}
        for i, component in enumerate(components):
            x = (i % 5) * 150  # Simple 5-column layout
            y = (i // 5) * 120
            positions[component.uuid] = ComponentPosition(x, y)
        return positions

class HierarchicalLayout:
    """Hierarchical layout based on component relationships"""
    
    def __init__(self, parameters: LayoutParameters):
        self.params = parameters
        self.logger = get_logger(__name__)
    
    def apply_layout(self, components: List[Component], 
                    connections: List[Connection] = None) -> Dict[str, ComponentPosition]:
        """Apply hierarchical layout based on connections"""
        try:
            if not components:
                return {}
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(components, connections or [])
            
            # Create layers based on dependencies
            layers = self._create_layers(components, dependency_graph)
            
            # Position components in layers
            positions = self._position_layers(layers)
            
            self.logger.info(f"Applied hierarchical layout with {len(layers)} layers")
            return positions
            
        except Exception as e:
            self.logger.error(f"Hierarchical layout failed: {e}")
            return GridLayout(self.params).apply_layout(components)
    
    def _build_dependency_graph(self, components: List[Component], 
                               connections: List[Connection]) -> Dict[str, Set[str]]:
        """Build component dependency graph from connections"""
        graph = {comp.uuid: set() for comp in components}
        
        for connection in connections:
            # Provider -> Requester dependency
            provider_uuid = connection.provider_endpoint.component_uuid
            requester_uuid = connection.requester_endpoint.component_uuid
            
            if provider_uuid in graph and requester_uuid in graph:
                graph[requester_uuid].add(provider_uuid)  # Requester depends on provider
        
        return graph
    
    def _create_layers(self, components: List[Component], 
                      dependency_graph: Dict[str, Set[str]]) -> List[List[Component]]:
        """Create layers of components based on dependencies"""
        component_map = {comp.uuid: comp for comp in components}
        layers = []
        placed = set()
        remaining = set(comp.uuid for comp in components)
        
        while remaining:
            # Find components with no unplaced dependencies
            current_layer = []
            
            for comp_uuid in list(remaining):
                dependencies = dependency_graph.get(comp_uuid, set())
                unplaced_deps = dependencies - placed
                
                if not unplaced_deps:  # All dependencies are placed
                    current_layer.append(component_map[comp_uuid])
                    remaining.remove(comp_uuid)
                    placed.add(comp_uuid)
            
            # If no progress, break cycles by adding remaining components
            if not current_layer and remaining:
                # Add components with fewest dependencies
                remaining_comps = [component_map[uuid] for uuid in remaining]
                remaining_comps.sort(key=lambda c: len(dependency_graph.get(c.uuid, set())))
                current_layer.append(remaining_comps[0])
                remaining.remove(remaining_comps[0].uuid)
                placed.add(remaining_comps[0].uuid)
            
            if current_layer:
                layers.append(current_layer)
        
        return layers
    
    def _position_layers(self, layers: List[List[Component]]) -> Dict[str, ComponentPosition]:
        """Position components within layers"""
        positions = {}
        
        for layer_index, layer_components in enumerate(layers):
            # Calculate layer position
            if self.params.hierarchy_direction == "top_down":
                layer_y = layer_index * self.params.layer_spacing
                layer_x_start = 0
            else:  # left_right
                layer_x = layer_index * self.params.layer_spacing
                layer_y_start = 0
            
            # Sort components in layer by type and connections
            sorted_components = self._sort_layer_components(layer_components)
            
            # Position components in layer
            for comp_index, component in enumerate(sorted_components):
                if self.params.hierarchy_direction == "top_down":
                    x = layer_x_start + comp_index * self.params.component_spacing_x
                    y = layer_y
                else:  # left_right
                    x = layer_x
                    y = layer_y_start + comp_index * self.params.component_spacing_y
                
                positions[component.uuid] = ComponentPosition(x, y)
        
        return positions
    
    def _sort_layer_components(self, components: List[Component]) -> List[Component]:
        """Sort components within a layer"""
        # Sort by type, then by port count, then by name
        type_priority = {
            ComponentType.COMPOSITION: 0,
            ComponentType.SERVICE: 1,
            ComponentType.APPLICATION: 2,
            ComponentType.SENSOR_ACTUATOR: 3,
            ComponentType.COMPLEX_DEVICE_DRIVER: 4
        }
        
        return sorted(components, key=lambda c: (
            type_priority.get(c.component_type, 5),
            -c.port_count,
            c.short_name or ""
        ))

class ForceDirectedLayout:
    """Force-directed layout algorithm (simplified spring model)"""
    
    def __init__(self, parameters: LayoutParameters):
        self.params = parameters
        self.logger = get_logger(__name__)
    
    def apply_layout(self, components: List[Component], 
                    connections: List[Connection] = None) -> Dict[str, ComponentPosition]:
        """Apply force-directed layout"""
        try:
            if not components:
                return {}
            
            if len(components) == 1:
                return {components[0].uuid: ComponentPosition(0, 0)}
            
            # Initialize random positions
            positions = self._initialize_random_positions(components)
            velocities = {comp.uuid: (0.0, 0.0) for comp in components}
            
            # Run simulation
            for iteration in range(self.params.iterations):
                forces = self._calculate_forces(components, connections or [], positions)
                positions, velocities = self._update_positions(components, positions, velocities, forces)
            
            # Convert to ComponentPosition objects
            result = {}
            for comp in components:
                x, y = positions[comp.uuid]
                result[comp.uuid] = ComponentPosition(x, y)
            
            self.logger.info(f"Applied force-directed layout with {self.params.iterations} iterations")
            return result
            
        except Exception as e:
            self.logger.error(f"Force-directed layout failed: {e}")
            return GridLayout(self.params).apply_layout(components)
    
    def _initialize_random_positions(self, components: List[Component]) -> Dict[str, Tuple[float, float]]:
        """Initialize components at random positions"""
        positions = {}
        area_size = math.sqrt(len(components)) * 200  # Rough area calculation
        
        for component in components:
            x = random.uniform(-area_size/2, area_size/2)
            y = random.uniform(-area_size/2, area_size/2)
            positions[component.uuid] = (x, y)
        
        return positions
    
    def _calculate_forces(self, components: List[Component], connections: List[Connection],
                         positions: Dict[str, Tuple[float, float]]) -> Dict[str, Tuple[float, float]]:
        """Calculate forces between components"""
        forces = {comp.uuid: (0.0, 0.0) for comp in components}
        
        # Repulsion forces (all pairs)
        for i, comp1 in enumerate(components):
            for comp2 in components[i+1:]:
                force_x, force_y = self._repulsion_force(positions[comp1.uuid], positions[comp2.uuid])
                
                # Apply force
                fx1, fy1 = forces[comp1.uuid]
                forces[comp1.uuid] = (fx1 + force_x, fy1 + force_y)
                
                fx2, fy2 = forces[comp2.uuid]
                forces[comp2.uuid] = (fx2 - force_x, fy2 - force_y)
        
        # Attraction forces (connected components)
        for connection in connections:
            provider_uuid = connection.provider_endpoint.component_uuid
            requester_uuid = connection.requester_endpoint.component_uuid
            
            if provider_uuid in positions and requester_uuid in positions:
                force_x, force_y = self._attraction_force(
                    positions[provider_uuid], positions[requester_uuid]
                )
                
                # Apply attraction force
                fx1, fy1 = forces[provider_uuid]
                forces[provider_uuid] = (fx1 + force_x, fy1 + force_y)
                
                fx2, fy2 = forces[requester_uuid]
                forces[requester_uuid] = (fx2 - force_x, fy2 - force_y)
        
        return forces
    
    def _repulsion_force(self, pos1: Tuple[float, float], 
                        pos2: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate repulsion force between two components"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:  # Avoid division by zero
            distance = 1
            dx, dy = random.uniform(-1, 1), random.uniform(-1, 1)
        
        force_magnitude = self.params.repulsion_force / (distance * distance)
        force_x = (dx / distance) * force_magnitude
        force_y = (dy / distance) * force_magnitude
        
        return force_x, force_y
    
    def _attraction_force(self, pos1: Tuple[float, float], 
                         pos2: Tuple[float, float]) -> Tuple[float, float]:
        """Calculate attraction force between connected components"""
        dx = pos2[0] - pos1[0]
        dy = pos2[1] - pos1[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1:
            return 0, 0
        
        force_magnitude = self.params.attraction_force * distance
        force_x = (dx / distance) * force_magnitude
        force_y = (dy / distance) * force_magnitude
        
        return force_x, force_y
    
    def _update_positions(self, components: List[Component], 
                         positions: Dict[str, Tuple[float, float]],
                         velocities: Dict[str, Tuple[float, float]],
                         forces: Dict[str, Tuple[float, float]]) -> Tuple[Dict, Dict]:
        """Update component positions based on forces"""
        new_positions = {}
        new_velocities = {}
        
        for component in components:
            uuid = component.uuid
            pos_x, pos_y = positions[uuid]
            vel_x, vel_y = velocities[uuid]
            force_x, force_y = forces[uuid]
            
            # Update velocity
            new_vel_x = (vel_x + force_x) * self.params.damping
            new_vel_y = (vel_y + force_y) * self.params.damping
            
            # Update position
            new_pos_x = pos_x + new_vel_x
            new_pos_y = pos_y + new_vel_y
            
            new_positions[uuid] = (new_pos_x, new_pos_y)
            new_velocities[uuid] = (new_vel_x, new_vel_y)
        
        return new_positions, new_velocities

class CircularLayout:
    """Circular layout algorithm"""
    
    def __init__(self, parameters: LayoutParameters):
        self.params = parameters
        self.logger = get_logger(__name__)
    
    def apply_layout(self, components: List[Component], 
                    connections: List[Connection] = None) -> Dict[str, ComponentPosition]:
        """Apply circular layout"""
        try:
            if not components:
                return {}
            
            if len(components) == 1:
                return {components[0].uuid: ComponentPosition(0, 0)}
            
            positions = {}
            
            # Sort components for better arrangement
            sorted_components = self._sort_components_for_circle(components, connections or [])
            
            # Calculate circle parameters
            num_components = len(sorted_components)
            angle_step = 2 * math.pi / num_components
            
            # Place components around circle
            for i, component in enumerate(sorted_components):
                angle = i * angle_step
                x = self.params.circle_radius * math.cos(angle)
                y = self.params.circle_radius * math.sin(angle)
                
                positions[component.uuid] = ComponentPosition(x, y)
            
            # Optionally place most connected component in center
            if self.params.center_important and connections:
                central_component = self._find_most_connected_component(components, connections)
                if central_component:
                    positions[central_component.uuid] = ComponentPosition(0, 0)
            
            self.logger.info(f"Applied circular layout for {num_components} components")
            return positions
            
        except Exception as e:
            self.logger.error(f"Circular layout failed: {e}")
            return GridLayout(self.params).apply_layout(components)
    
    def _sort_components_for_circle(self, components: List[Component], 
                                   connections: List[Connection]) -> List[Component]:
        """Sort components for better circular arrangement"""
        # Sort by connection count, then by type
        connection_counts = self._calculate_connection_counts(components, connections)
        
        return sorted(components, key=lambda c: (
            -connection_counts.get(c.uuid, 0),  # Most connected first
            c.component_type.value,
            c.short_name or ""
        ))
    
    def _calculate_connection_counts(self, components: List[Component], 
                                   connections: List[Connection]) -> Dict[str, int]:
        """Calculate connection count for each component"""
        counts = {comp.uuid: 0 for comp in components}
        
        for connection in connections:
            provider_uuid = connection.provider_endpoint.component_uuid
            requester_uuid = connection.requester_endpoint.component_uuid
            
            if provider_uuid in counts:
                counts[provider_uuid] += 1
            if requester_uuid in counts:
                counts[requester_uuid] += 1
        
        return counts
    
    def _find_most_connected_component(self, components: List[Component], 
                                     connections: List[Connection]) -> Optional[Component]:
        """Find the component with most connections"""
        connection_counts = self._calculate_connection_counts(components, connections)
        
        if not connection_counts:
            return None
        
        most_connected_uuid = max(connection_counts, key=connection_counts.get)
        return next((comp for comp in components if comp.uuid == most_connected_uuid), None)

class LayoutEngine:
    """Main layout engine that coordinates different algorithms"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.parameters = LayoutParameters()
        
        # Available algorithms
        self.algorithms = {
            LayoutType.GRID: GridLayout(self.parameters),
            LayoutType.HIERARCHICAL: HierarchicalLayout(self.parameters),
            LayoutType.FORCE_DIRECTED: ForceDirectedLayout(self.parameters),
            LayoutType.CIRCULAR: CircularLayout(self.parameters)
        }
    
    def apply_layout(self, components: List[Component], connections: List[Connection] = None,
                    layout_type: LayoutType = LayoutType.HIERARCHICAL) -> Dict[str, ComponentPosition]:
        """Apply specified layout algorithm"""
        try:
            if not components:
                return {}
            
            algorithm = self.algorithms.get(layout_type)
            if not algorithm:
                self.logger.warning(f"Unknown layout type: {layout_type}, using grid")
                algorithm = self.algorithms[LayoutType.GRID]
            
            positions = algorithm.apply_layout(components, connections)
            
            # Post-process positions
            positions = self._post_process_positions(positions)
            
            self.logger.info(f"Applied {layout_type.value} layout to {len(components)} components")
            return positions
            
        except Exception as e:
            self.logger.error(f"Layout engine failed: {e}")
            return self._emergency_layout(components)
    
    def _post_process_positions(self, positions: Dict[str, ComponentPosition]) -> Dict[str, ComponentPosition]:
        """Post-process positions to ensure they're all positive and well-spaced"""
        if not positions:
            return positions
        
        # Find minimum coordinates
        min_x = min(pos.x for pos in positions.values())
        min_y = min(pos.y for pos in positions.values())
        
        # Shift all positions to ensure positive coordinates
        margin = 50
        if min_x < margin:
            x_offset = margin - min_x
        else:
            x_offset = 0
        
        if min_y < margin:
            y_offset = margin - min_y
        else:
            y_offset = 0
        
        # Apply offset
        for uuid, pos in positions.items():
            positions[uuid] = ComponentPosition(
                pos.x + x_offset,
                pos.y + y_offset,
                pos.width,
                pos.height
            )
        
        return positions
    
    def _emergency_layout(self, components: List[Component]) -> Dict[str, ComponentPosition]:
        """Emergency fallback layout"""
        positions = {}
        for i, component in enumerate(components):
            x = (i % 3) * 200  # Simple 3-column layout
            y = (i // 3) * 150
            positions[component.uuid] = ComponentPosition(x, y)
        return positions
    
    def set_parameters(self, **kwargs):
        """Update layout parameters"""
        for key, value in kwargs.items():
            if hasattr(self.parameters, key):
                setattr(self.parameters, key, value)
        
        # Update all algorithms with new parameters
        self.algorithms = {
            LayoutType.GRID: GridLayout(self.parameters),
            LayoutType.HIERARCHICAL: HierarchicalLayout(self.parameters),
            LayoutType.FORCE_DIRECTED: ForceDirectedLayout(self.parameters),
            LayoutType.CIRCULAR: CircularLayout(self.parameters)
        }
    
    def get_layout_info(self) -> Dict[str, Any]:
        """Get information about available layouts and current parameters"""
        return {
            'available_layouts': [layout.value for layout in LayoutType],
            'parameters': {
                'component_spacing_x': self.parameters.component_spacing_x,
                'component_spacing_y': self.parameters.component_spacing_y,
                'layer_spacing': self.parameters.layer_spacing,
                'grid_columns': self.parameters.grid_columns,
                'hierarchy_direction': self.parameters.hierarchy_direction,
                'circle_radius': self.parameters.circle_radius
            }
        }

# Utility functions
def calculate_optimal_spacing(num_components: int, available_area: Tuple[float, float]) -> Tuple[float, float]:
    """Calculate optimal spacing for given number of components and area"""
    area_width, area_height = available_area
    
    # Calculate grid dimensions
    cols = math.ceil(math.sqrt(num_components))
    rows = math.ceil(num_components / cols)
    
    # Calculate spacing
    spacing_x = area_width / max(1, cols - 1) if cols > 1 else area_width
    spacing_y = area_height / max(1, rows - 1) if rows > 1 else area_height
    
    # Ensure minimum spacing
    min_spacing = 100
    spacing_x = max(min_spacing, spacing_x)
    spacing_y = max(min_spacing, spacing_y)
    
    return spacing_x, spacing_y

def detect_best_layout(components: List[Component], connections: List[Connection] = None) -> LayoutType:
    """Detect the best layout algorithm for given components and connections"""
    num_components = len(components)
    num_connections = len(connections) if connections else 0
    
    # Decision logic
    if num_components <= 1:
        return LayoutType.GRID
    elif num_components <= 6:
        if num_connections > 0:
            return LayoutType.CIRCULAR
        else:
            return LayoutType.GRID
    elif num_connections > num_components * 0.5:
        # Highly connected - use force-directed
        return LayoutType.FORCE_DIRECTED
    elif num_connections > 0:
        # Some connections - use hierarchical
        return LayoutType.HIERARCHICAL
    else:
        # No connections - use grid
        return LayoutType.GRID