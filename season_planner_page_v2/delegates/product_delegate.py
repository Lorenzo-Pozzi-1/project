"""
Product Delegate for Season Planner V2.

QStyledItemDelegate that provides product selection through a modal dialog.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QDialog
from PySide6.QtCore import Qt, QEvent
from common.widgets.product_selection import ProductSelectionWidget


class ProductSelectionDialog(QDialog):
    """Modal dialog for product selection."""
    
    def __init__(self, parent=None, current_product=""):
        """Initialize the product selection dialog."""
        super().__init__(parent)
        self.selected_product = current_product
        self.setWindowTitle("Select Product")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QLabel
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel("Select a pesticide product:")
        layout.addWidget(instructions)
        
        # Product selection widget
        self.product_widget = ProductSelectionWidget(
            orientation='vertical',
            show_labels=True
        )
        
        # Set current product if provided
        if self.selected_product:
            self.product_widget.set_selected_product(self.selected_product)
        
        # Connect selection signal
        self.product_widget.product_selected.connect(self.on_product_selected)
        
        layout.addWidget(self.product_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(bool(self.selected_product))
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def on_product_selected(self, product_name):
        """Handle product selection."""
        self.selected_product = product_name
        self.ok_button.setEnabled(bool(product_name))
    
    def get_selected_product(self):
        """Get the selected product name."""
        return self.selected_product


class ProductDelegate(QStyledItemDelegate):
    """
    Delegate for product selection with modal dialog.
    
    Displays product names as text and opens a product selection dialog
    when editing is initiated.
    """
    
    def __init__(self, parent=None):
        """Initialize the product delegate."""
        super().__init__(parent)
    
    def createEditor(self, parent, option, index):
        """Create the product selection dialog."""
        current_value = index.data(Qt.EditRole) or ""
        
        dialog = ProductSelectionDialog(parent, current_value)
        return dialog
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        # Data is already set in createEditor
        pass
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if isinstance(editor, ProductSelectionDialog):
            if editor.exec() == QDialog.Accepted:
                selected_product = editor.get_selected_product()
                if selected_product:
                    model.setData(index, selected_product, Qt.EditRole)
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry - center the dialog."""
        if isinstance(editor, ProductSelectionDialog):
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