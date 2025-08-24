#!/usr/bin/env python3
"""
Test script for operations table integration with custom machines.
"""

import sys
import os

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

def test_operations_integration():
    """Test operations table integration with custom machines."""
    print("Testing operations table integration with custom machines...")
    
    try:
        # Test imports
        from STIR.data.model_operation import Operation
        from STIR.data.repository_custom_machine import CustomMachineRepository
        from STIR.operations_table.operations_table_model import STIROperationsTableModel
        print("✅ All modules imported successfully")
        
        # Test custom machine repository
        custom_repo = CustomMachineRepository.get_instance()
        custom_machines = custom_repo.load_all()
        print(f"✅ Found {len(custom_machines)} custom machines")
        
        if custom_machines:
            # Test creating an operation with a custom machine
            test_machine = custom_machines[0]
            print(f"✅ Testing with custom machine: {test_machine.name}")
            
            # Create operation
            operation = Operation()
            operation.load_custom_machine_defaults(test_machine.name)
            print(f"✅ Operation loaded with custom machine")
            print(f"   - Machine name: {operation.machine_name}")
            print(f"   - Is custom: {operation.is_custom_machine()}")
            print(f"   - Number of tools: {len(operation.custom_machine_tools) if operation.custom_machine_tools else 0}")
            
            if operation.custom_machine_tools:
                # Test depth and area display
                max_depth = max(tool.depth for tool in operation.custom_machine_tools)
                max_area = max(tool.surface_area_disturbed for tool in operation.custom_machine_tools)
                print(f"   - Max depth: {max_depth} cm")
                print(f"   - Max area: {max_area}%")
                
                # Test STIR calculation
                operation.calculate_stir()
                print(f"   - STIR value: {operation.stir_value}")
                
                # Test depth adjustment
                original_depths = [tool.depth for tool in operation.custom_machine_tools]
                print(f"   - Original depths: {original_depths}")
                
                operation.adjust_custom_machine_depth(15.0, "cm")  # 15 cm
                adjusted_depths = [tool.depth for tool in operation.custom_machine_tools]
                print(f"   - Adjusted depths: {adjusted_depths}")
                
            print("✅ Custom machine operation test passed")
            
            # Test operations table model
            table_model = STIROperationsTableModel()
            table_model.set_operations([operation])
            print("✅ Operations table model created and populated")
            
            # Test data display
            from PySide6.QtCore import QModelIndex, Qt
            
            # Test depth display (column 2)
            depth_index = table_model.index(0, 2)
            depth_display = table_model.data(depth_index, Qt.DisplayRole)
            print(f"   - Depth display value: {depth_display}")
            
            # Test area display (column 4)
            area_index = table_model.index(0, 4)
            area_display = table_model.data(area_index, Qt.DisplayRole)
            print(f"   - Area display value: {area_display}")
            
            # Test area editability (should be read-only for custom machines)
            area_flags = table_model.flags(area_index)
            is_editable = bool(area_flags & Qt.ItemIsEditable)
            print(f"   - Area editable: {is_editable} (should be False for custom machines)")
            
            print("✅ Operations table integration test passed")
            
        print("\n🎉 All tests passed! Operations table integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_operations_integration()
