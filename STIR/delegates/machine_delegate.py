"""
Machine Selection Delegate for STIR Operations Table.

Provides a visual dialog for selecting machines using pictures.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QPushButton, QWidget, QHBoxLayout, QDialog
from PySide6.QtCore import Qt
from ..machine_selection_dialog import MachineSelectionDialog
from ..repository_machine import MachineRepository


class MachineSelectionDelegate(QStyledItemDelegate):
    """Custom delegate for machine selection with visual dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.machine_repo = MachineRepository.get_instance()
    
    def createEditor(self, parent, option, index):
        """Create a button that opens the machine selection dialog."""
        # Create a container widget
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the button
        button = QPushButton("Select Machine...", container)
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ccc;
            }
            QPushButton:hover {
                border: 2px solid #007ACC;
            }
        """)
        
        # Set current machine name if available
        current_text = index.model().data(index, Qt.EditRole) or ""
        if current_text:
            button.setText(current_text)
        
        # Connect button click to open dialog
        button.clicked.connect(lambda: self.open_selection_dialog(button, index))
        
        layout.addWidget(button)
        container.button = button  # Store reference for later access
        
        # Auto-open the dialog
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.open_selection_dialog(button, index))
        
        return container
    
    def open_selection_dialog(self, button, index):
        """Open the machine selection dialog."""
        current_machine = index.model().data(index, Qt.EditRole) or ""
        
        dialog = MachineSelectionDialog(button.parent(), current_machine)
        if dialog.exec() == QDialog.Accepted:
            selected_machine = dialog.get_selected_machine()
            button.setText(selected_machine)
            # Update the model data
            index.model().setData(index, selected_machine, Qt.EditRole)
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        current_text = index.model().data(index, Qt.EditRole) or ""
        if hasattr(editor, 'button'):
            if current_text:
                editor.button.setText(current_text)
            else:
                editor.button.setText("Select Machine...")
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if hasattr(editor, 'button'):
            selected_machine = editor.button.text()
            if selected_machine != "Select Machine...":
                model.setData(index, selected_machine, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry."""
        editor.setGeometry(option.rect)