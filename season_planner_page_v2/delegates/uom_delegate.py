"""
UOM Delegate for Season Planner V2.

QStyledItemDelegate that provides UOM selection through a modal dialog.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QDialog
from PySide6.QtCore import Qt, QEvent
from common.widgets.UOM_selector import SmartUOMSelector


class UOMSelectionDialog(QDialog):
    """Modal dialog for UOM selection."""
    
    def __init__(self, parent=None, current_uom="", uom_type="application_rate"):
        """Initialize the UOM selection dialog."""
        super().__init__(parent)
        self.selected_uom = current_uom
        self.uom_type = uom_type
        self.setWindowTitle("Select Unit of Measure")
        self.setModal(True)
        self.setMinimumSize(300, 200)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        layout = QVBoxLayout(self)
        
        # Instructions
        category_name = self.uom_type.replace("_", " ").title()
        instructions = QLabel(f"Select {category_name} unit:")
        layout.addWidget(instructions)
        
        # UOM selector
        self.uom_selector = SmartUOMSelector(uom_type=self.uom_type)
        
        # Set current UOM if provided
        if self.selected_uom:
            self.uom_selector.setCurrentText(self.selected_uom)
        
        # Connect selection signal
        self.uom_selector.currentTextChanged.connect(self.on_uom_selected)
        
        layout.addWidget(self.uom_selector)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(bool(self.selected_uom))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def on_uom_selected(self, uom):
        """Handle UOM selection."""
        self.selected_uom = uom
        self.ok_button.setEnabled(bool(uom))
    
    def get_selected_uom(self):
        """Get the selected UOM."""
        return self.selected_uom


class UOMDelegate(QStyledItemDelegate):
    """
    Delegate for UOM selection with modal dialog.
    
    Displays UOM as text and opens a UOM selection dialog
    when editing is initiated.
    """
    
    def __init__(self, parent=None, uom_type="application_rate"):
        """Initialize the UOM delegate."""
        super().__init__(parent)
        self.uom_type = uom_type
    
    def createEditor(self, parent, option, index):
        """Create the UOM selection dialog."""
        current_value = index.data(Qt.EditRole) or ""
        
        dialog = UOMSelectionDialog(parent, current_value, self.uom_type)
        return dialog
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        # Data is already set in createEditor
        pass
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if isinstance(editor, UOMSelectionDialog):
            if editor.exec() == QDialog.Accepted:
                selected_uom = editor.get_selected_uom()
                if selected_uom:
                    # Handle rate conversion if this is a rate UOM change
                    if self.uom_type == "application_rate":
                        self._handle_rate_conversion(editor, model, index, selected_uom)
                    else:
                        model.setData(index, selected_uom, Qt.EditRole)
    
    def _handle_rate_conversion(self, editor, model, index, new_uom):
        """Handle automatic rate conversion when UOM changes."""
        from common import get_config
        from data.repository_UOM import UOMRepository, CompositeUOM
        
        # Get current rate and UOM
        rate_col = index.column() - 1  # Assuming rate column is just before UOM column
        current_uom = index.data(Qt.EditRole) or ""
        
        if rate_col >= 0:
            rate_index = model.index(index.row(), rate_col)
            current_rate = rate_index.data(Qt.EditRole) or 0.0
            
            if current_rate > 0 and current_uom and new_uom != current_uom:
                try:
                    # Perform UOM conversion
                    uom_repo = UOMRepository.get_instance()
                    user_preferences = get_config("user_preferences", {})
                    
                    from_composite = CompositeUOM(current_uom)
                    to_composite = CompositeUOM(new_uom)
                    
                    converted_rate = uom_repo.convert_composite_uom(
                        current_rate, from_composite, to_composite, user_preferences
                    )
                    
                    # Update both rate and UOM
                    model.setData(rate_index, converted_rate, Qt.EditRole)
                    model.setData(index, new_uom, Qt.EditRole)
                    
                except Exception as e:
                    # If conversion fails, just update the UOM
                    print(f"UOM conversion failed: {e}")
                    model.setData(index, new_uom, Qt.EditRole)
            else:
                # No conversion needed, just update UOM
                model.setData(index, new_uom, Qt.EditRole)
        else:
            # Can't find rate column, just update UOM
            model.setData(index, new_uom, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry - center the dialog."""
        if isinstance(editor, UOMSelectionDialog):
            # Center the dialog on the parent widget
            if editor.parent():
                parent_rect = editor.parent().geometry()
                dialog_size = editor.sizeHint()
                x = parent_rect.x() + (parent_rect.width() - dialog_size.width()) // 2
                y = parent_rect.y() + (parent_rect.height() - dialog_size.height()) // 2
                editor.setGeometry(x, y, dialog_size.width(), dialog_size.height())
    
    def editorEvent(self, event, model, option, index):
        """Handle editor events."""
        # Handle double-click to open dialog
        if event.type() == QEvent.MouseButtonDblClick:
            self.createEditor(option.widget, option, index).exec()
            return True
        
        return super().editorEvent(event, model, option, index)