"""
Fixed UOM Delegate for Season Planner V2.

QStyledItemDelegate that provides UOM selection through a combobox
with automatic rate conversion functionality.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QComboBox
from PySide6.QtCore import Qt
from common.widgets.UOM_selector import UOM_CATEGORIES
from common import get_config
from data.repository_UOM import UOMRepository, CompositeUOM


class UOMDelegate(QStyledItemDelegate):
    """
    Fixed delegate for UOM selection using a combobox.
    
    Provides UOM selection and handles automatic rate conversion
    when application rate UOMs change.
    """
    
    def __init__(self, parent=None, uom_type="application_rate"):
        """Initialize the UOM delegate."""
        super().__init__(parent)
        self.uom_type = uom_type
        self._uom_list = UOM_CATEGORIES.get(uom_type, [])
    
    def createEditor(self, parent, option, index):
        """Create a QComboBox editor with appropriate UOMs."""
        editor = QComboBox(parent)
        editor.setEditable(True)
        editor.setInsertPolicy(QComboBox.NoInsert)
        
        # Add empty option first, then all UOMs for this type
        editor.addItem("")  # Empty option
        editor.addItems(self._uom_list)
        
        # Set placeholder text
        editor.lineEdit().setPlaceholderText("Select unit...")
        
        return editor
    
    def setEditorData(self, editor, index):
        """Set the current data in the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        value = index.data(Qt.EditRole) or ""
        
        # Try to find exact match first
        index_in_combo = editor.findText(value, Qt.MatchExactly)
        if index_in_combo >= 0:
            editor.setCurrentIndex(index_in_combo)
        else:
            # Set custom text (for imported or custom UOMs)
            editor.setEditText(value)
    
    def setModelData(self, editor, model, index):
        """Set the model data from the editor."""
        if not isinstance(editor, QComboBox):
            return
        
        new_uom = editor.currentText().strip()
        
        # Handle rate conversion for application rate UOMs
        if self.uom_type == "application_rate" and new_uom:
            success = self._handle_rate_conversion(model, index, new_uom)
            if not success:
                # If conversion failed, still update the UOM
                model.setData(index, new_uom, Qt.EditRole)
        else:
            # For non-rate UOMs, just update directly
            model.setData(index, new_uom, Qt.EditRole)
    
    def _handle_rate_conversion(self, model, uom_index, new_uom):
        """
        Handle automatic rate conversion when UOM changes.
        
        Args:
            model: The table model
            uom_index: QModelIndex for the UOM cell
            new_uom: New UOM string
            
        Returns:
            bool: True if conversion was successful, False otherwise
        """
        try:
            # Get current UOM
            current_uom = uom_index.data(Qt.EditRole) or ""
            
            # Skip if UOM hasn't actually changed
            if current_uom == new_uom:
                return True
            
            # Find the rate column - use model's column constants for safety
            rate_col = None
            if hasattr(model, 'COL_RATE') and hasattr(model, 'COL_RATE_UOM'):
                if uom_index.column() == model.COL_RATE_UOM:
                    rate_col = model.COL_RATE
            
            if rate_col is None:
                print("Could not determine rate column for UOM conversion")
                model.setData(uom_index, new_uom, Qt.EditRole)
                return False
            
            # Get current rate
            rate_index = model.index(uom_index.row(), rate_col)
            current_rate = rate_index.data(Qt.EditRole) or 0.0
            
            # Skip conversion if rate is 0 or no current UOM
            if current_rate <= 0 or not current_uom:
                model.setData(uom_index, new_uom, Qt.EditRole)
                return True
            
            # Perform UOM conversion
            converted_rate = self._convert_rate(current_rate, current_uom, new_uom)
            
            if converted_rate is not None:
                # Update both rate and UOM
                model.setData(rate_index, converted_rate, Qt.EditRole)
                model.setData(uom_index, new_uom, Qt.EditRole)
                
                print(f"Auto-converted rate: {current_rate} {current_uom} → {converted_rate:.2f} {new_uom}")
                return True
            else:
                # Conversion failed - just update UOM
                model.setData(uom_index, new_uom, Qt.EditRole)
                return False
                
        except Exception as e:
            print(f"Error in rate conversion: {e}")
            model.setData(uom_index, new_uom, Qt.EditRole)
            return False
    
    def _convert_rate(self, value, from_uom, to_uom):
        """
        Convert rate value between UOMs.
        
        Args:
            value (float): Rate value to convert
            from_uom (str): Source UOM
            to_uom (str): Target UOM
            
        Returns:
            float or None: Converted value or None if conversion failed
        """
        if not from_uom or not to_uom or from_uom == to_uom:
            return value
        
        try:
            # Get UOM repository and user preferences
            uom_repo = UOMRepository.get_instance()
            user_preferences = get_config("user_preferences", {})
            
            # Create composite UOM objects
            from_composite = CompositeUOM(from_uom)
            to_composite = CompositeUOM(to_uom)
            
            # Perform conversion
            converted_value = uom_repo.convert_composite_uom(
                value, from_composite, to_composite, user_preferences
            )
            
            return converted_value
            
        except Exception as e:
            print(f"UOM conversion failed: {from_uom} → {to_uom}: {e}")
            return None
    
    def updateEditorGeometry(self, editor, option, index):
        """Update editor geometry to match the cell."""
        editor.setGeometry(option.rect)
    
    def displayText(self, value, locale):
        """Format the display text."""
        if value is None or str(value).strip() == "":
            return ""
        return str(value)