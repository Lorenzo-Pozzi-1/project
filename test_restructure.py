#!/usr/bin/env python3
"""
Test script to verify all imports and paths work correctly after restructuring.
"""

import sys
import os

# Add the app directory to the Python path
app_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, app_dir)

def test_restructure():
    """Test that all imports and paths work correctly."""
    try:
        print("Testing imports after restructure...")
        
        # Test data models
        from STIR.data.model_operation import Operation
        from STIR.data.model_machine import Machine
        from STIR.data.model_custom_machine import CustomMachine, CustomMachineTool
        print("✅ Data models import successfully")
        
        # Test repositories
        from STIR.data.repository_machine import MachineRepository
        from STIR.data.repository_custom_machine import CustomMachineRepository
        print("✅ Repositories import successfully")
        
        # Test operations table
        from STIR.operations_table.operations_table_model import STIROperationsTableModel
        from STIR.operations_table.widget_operations_table import STIROperationsTableWidget
        print("✅ Operations table components import successfully")
        
        # Test dialogs
        from STIR.dialogs.custom_machine_manager_dialog import CustomMachineManagerDialog
        from STIR.dialogs.new_custom_machine_dialog import NewCustomMachineDialog
        from STIR.dialogs.machine_selection_dialog import MachineSelectionDialog
        print("✅ Dialogs import successfully")
        
        # Test delegates
        from STIR.delegates.machine_delegate import MachineSelectionDelegate
        from STIR.delegates.group_delegate import GroupSelectionDelegate
        from STIR.delegates.numeric_delegate import NumericDelegate
        print("✅ Delegates import successfully")
        
        # Test CSV paths
        repo = CustomMachineRepository.get_instance()
        machines = repo.load_all()
        print(f"✅ Custom machines CSV loads correctly: {len(machines)} machines")
        
        machine_repo = MachineRepository.get_instance()
        regular_machines = machine_repo.get_all_machines()
        print(f"✅ Regular machines CSV loads correctly: {len(regular_machines)} machines")
        
        # Test image paths exist
        from common.utils import resource_path
        custom_images_dir = resource_path("STIR/data/images/custom_machines")
        regular_images_dir = resource_path("STIR/data/images/machines")
        
        print(f"✅ Custom images directory exists: {os.path.exists(custom_images_dir)}")
        print(f"✅ Regular images directory exists: {os.path.exists(regular_images_dir)}")
        
        if machines:
            # Test a specific machine image path
            test_machine = machines[0]
            if test_machine.picture:
                image_path = resource_path(f"STIR/data/images/custom_machines/{test_machine.picture}")
                print(f"✅ Test image path exists: {os.path.exists(image_path)} ({test_machine.picture})")
        
        print("\n🎉 All restructure tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_restructure()
