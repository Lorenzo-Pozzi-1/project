"""
Custom Machine model for STIR calculations.

This module defines the CustomMachine class which represents a custom tillage machine
with multiple tools, each having their own operational parameters.
"""

from typing import Dict, Any, List, Optional
from .model_machine import Machine


class CustomMachineTool:
    """
    Represents a single tool on a custom machine.
    
    Each tool has its own operational parameters for STIR calculations.
    """
    
    def __init__(self,
                 name: str = "",
                 rotates: bool = False,
                 depth: float = 0.0,
                 depth_uom: str = "cm",
                 surface_area_disturbed: float = 100.0,
                 tillage_type_factor: float = 0.0):
        """
        Initialize a CustomMachineTool.
        
        Args:
            name: Name of the tool (e.g., "Primary Disc", "Chisel", etc.)
            rotates: Whether the tool has rotating/powered components (True/False)
            depth: Working depth of the tool
            depth_uom: Unit of measure for depth (e.g., "cm", "in")
            surface_area_disturbed: Percentage of surface area disturbed by this tool (0-100)
            tillage_type_factor: Tillage intensity factor for this tool (1.0=Inversion+mixing, 
                               0.8=Mixing+some inversion, 0.7=Mixing only, 0.4=Lifting+fracturing, 
                               0.15=Compression)
        """
        self.name = name
        self.rotates = rotates
        self.depth = depth
        self.depth_uom = depth_uom
        self.surface_area_disturbed = surface_area_disturbed
        self.tillage_type_factor = tillage_type_factor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation."""
        return {
            "name": self.name,
            "rotates": self.rotates,
            "depth": self.depth,
            "depth_uom": self.depth_uom,
            "surface_area_disturbed": self.surface_area_disturbed,
            "tillage_type_factor": self.tillage_type_factor
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomMachineTool':
        """Create CustomMachineTool instance from dictionary."""
        return cls(
            name=data.get("name", ""),
            rotates=data.get("rotates", False),
            depth=data.get("depth", 0.0),
            depth_uom=data.get("depth_uom", "cm"),
            surface_area_disturbed=data.get("surface_area_disturbed", 100.0),
            tillage_type_factor=data.get("tillage_type_factor", 0.0)
        )
    
    def is_empty(self) -> bool:
        """Check if this tool has any meaningful data."""
        return (not self.name.strip() and 
                self.depth == 0.0 and 
                self.surface_area_disturbed == 100.0 and 
                self.tillage_type_factor == 0.0)


class CustomMachine:
    """
    Represents a custom tillage machine with multiple tools for STIR calculations.
    
    A custom machine can have up to 10 tools, each with their own operational parameters.
    The total STIR is calculated by summing the STIR values from all active tools.
    """
    
    def __init__(self,
                 name: str = "",
                 speed: float = 0.0,
                 speed_uom: str = "km/h",
                 picture: str = "",
                 notes: str = "",
                 tools: List[CustomMachineTool] = None):
        """
        Initialize a CustomMachine.
        
        Args:
            name: Name of the custom machine
            speed: Operating speed of the machine
            speed_uom: Unit of measure for speed (e.g., "km/h", "mph")
            picture: Filename of the machine picture
            notes: Notes/description for the custom machine
            tools: List of CustomMachineTool objects (up to 10)
        """
        self.name = name
        self.speed = speed
        self.speed_uom = speed_uom
        self.picture = picture
        self.notes = notes
        self.tools = tools if tools is not None else []
        
        # Ensure we don't exceed 10 tools
        if len(self.tools) > 10:
            self.tools = self.tools[:10]
    
    def add_tool(self, tool: CustomMachineTool) -> bool:
        """
        Add a tool to the custom machine.
        
        Args:
            tool: CustomMachineTool to add
            
        Returns:
            bool: True if tool was added, False if machine already has 10 tools
        """
        if len(self.tools) < 10:
            self.tools.append(tool)
            return True
        return False
    
    def remove_tool(self, index: int) -> bool:
        """
        Remove a tool at the specified index.
        
        Args:
            index: Index of the tool to remove
            
        Returns:
            bool: True if tool was removed, False if index is invalid
        """
        if 0 <= index < len(self.tools):
            self.tools.pop(index)
            return True
        return False
    
    def get_active_tools(self) -> List[CustomMachineTool]:
        """Get list of tools that have meaningful data (not empty)."""
        return [tool for tool in self.tools if not tool.is_empty()]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert custom machine to dictionary representation.
        
        Returns:
            dict: Custom machine data as dictionary
        """
        result = {
            "name": self.name,
            "speed": self.speed,
            "speed_uom": self.speed_uom,
            "picture": self.picture,
            "notes": self.notes
        }
        
        # Add tool data (up to 10 tools)
        for i in range(10):
            tool_prefix = f"tool{i+1}_"
            if i < len(self.tools):
                tool = self.tools[i]
                result[f"{tool_prefix}name"] = tool.name
                result[f"{tool_prefix}rotates"] = tool.rotates
                result[f"{tool_prefix}depth"] = tool.depth
                result[f"{tool_prefix}depth_uom"] = tool.depth_uom
                result[f"{tool_prefix}surface_area_disturbed"] = tool.surface_area_disturbed
                result[f"{tool_prefix}tillage_type_factor"] = tool.tillage_type_factor
            else:
                # Fill empty slots with default values
                result[f"{tool_prefix}name"] = ""
                result[f"{tool_prefix}rotates"] = ""
                result[f"{tool_prefix}depth"] = ""
                result[f"{tool_prefix}depth_uom"] = ""
                result[f"{tool_prefix}surface_area_disturbed"] = ""
                result[f"{tool_prefix}tillage_type_factor"] = ""
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CustomMachine':
        """
        Create CustomMachine instance from dictionary.
        
        Args:
            data: Dictionary containing custom machine data
            
        Returns:
            CustomMachine: New CustomMachine instance
        """
        # Extract basic machine info
        name = data.get("name", "")
        speed = float(data.get("speed", 0.0)) if data.get("speed") else 0.0
        speed_uom = data.get("speed_uom", "km/h")
        picture = data.get("picture", "")
        notes = data.get("notes", "")
        
        # Extract tools
        tools = []
        for i in range(10):
            tool_prefix = f"tool{i+1}_"
            
            # Check if this tool slot has data
            name_key = f"{tool_prefix}name"
            rotates_key = f"{tool_prefix}rotates"
            depth_key = f"{tool_prefix}depth"
            
            if name_key in data and rotates_key in data and depth_key in data:
                name_val = data.get(name_key)
                rotates_val = data.get(rotates_key)
                depth_val = data.get(depth_key)
                
                # Skip empty tool slots
                if not name_val or rotates_val == "" or depth_val == "":
                    continue
                
                # Convert string values to appropriate types
                try:
                    name = str(name_val).strip()
                    rotates = str(rotates_val).upper() == "TRUE"
                    depth = float(depth_val)
                    depth_uom = data.get(f"{tool_prefix}depth_uom", "cm")
                    surface_area_disturbed = float(data.get(f"{tool_prefix}surface_area_disturbed", 100.0))
                    tillage_type_factor = float(data.get(f"{tool_prefix}tillage_type_factor", 0.0))
                    
                    tool = CustomMachineTool(
                        name=name,
                        rotates=rotates,
                        depth=depth,
                        depth_uom=depth_uom,
                        surface_area_disturbed=surface_area_disturbed,
                        tillage_type_factor=tillage_type_factor
                    )
                    tools.append(tool)
                except (ValueError, TypeError):
                    # Skip invalid tool data
                    continue
        
        return cls(
            name=name,
            speed=speed,
            speed_uom=speed_uom,
            picture=picture,
            notes=notes,
            tools=tools
        )
    
    def create_operations_for_tools(self, operation_group: str = "pre-plant"):
        """
        Create separate Operations for each active tool on this custom machine.
        
        Args:
            operation_group: Type of operation ("pre-plant", "in-season", "harvest")
            
        Returns:
            List[Operation]: List of Operation instances, one for each active tool
        """
        from .model_operation import Operation
        
        operations = []
        active_tools = self.get_active_tools()
        
        for i, tool in enumerate(active_tools):
            tool_name = f"{self.name} - Tool {i+1}"
            
            operation = Operation(
                operation_group=operation_group,
                machine_name=tool_name,
                depth=tool.depth,
                depth_uom=tool.depth_uom,
                speed=self.speed,
                speed_uom=self.speed_uom,
                surface_area_disturbed=tool.surface_area_disturbed,
                tillage_type_factor=tool.tillage_type_factor,
                machine_rotates=tool.rotates
            )
            operations.append(operation)
        
        return operations
    
    def calculate_total_stir(self) -> float:
        """
        Calculate the total STIR value for this custom machine.
        
        This is the sum of STIR values from all active tools.
        Note: This method assumes the STIR calculation logic exists in the Operation class.
        
        Returns:
            float: Total STIR value for the custom machine
        """
        operations = self.create_operations_for_tools()
        total_stir = 0.0
        
        for operation in operations:
            # Assuming Operation has a calculate_stir method
            if hasattr(operation, 'calculate_stir'):
                total_stir += operation.calculate_stir()
        
        return total_stir
    
    def __str__(self) -> str:
        """Return string representation of the custom machine."""
        active_count = len(self.get_active_tools())
        return f"CustomMachine: {self.name} ({active_count} tools)"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the custom machine."""
        return (f"CustomMachine(name='{self.name}', speed={self.speed}, "
                f"tools_count={len(self.tools)})")
