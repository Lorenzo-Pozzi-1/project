"""
Machine Selection Delegate for STIR Operations Table.

Provides a QComboBox for selecting machines from the machine repository.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from PySide6.QtCore import Qt
from ..repository_machine import MachineRepository


class MachineSelectionDelegate(QStyledItemDelegate):
    """Custom delegate for machine selection with QComboBox."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.machine_repo = MachineRepository.get_instance()
    
    def createEditor(self, parent, option, index):
        """Create a QComboBox editor with available machines."""
        editor = QComboBox(parent)
        editor.setEditable(False)
        
        # Add empty option
        editor.addItem("")
        
        # Add all available machines
        machines = self.machine_repo.get_all_machines()
        for machine in machines:
            editor.addItem(machine.name)
        
        # Schedule the dropdown to open after the editor is fully created
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, editor.showPopup)
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        current_text = index.model().data(index, Qt.EditRole) or ""
        editor.setCurrentText(current_text)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        selected_machine = editor.currentText()
        model.setData(index, selected_machine, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)