"""
Fixed UOM Delegate for Season Planner V2.

QStyledItemDelegate that provides UOM selection through a dialog
with automatic rate conversion functionality.
"""
from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QDialog
from common import get_config
from common.widgets.UOM_selector import UOMSelectionDialog, UOM_CATEGORIES
from data.repository_UOM import UOMRepository, CompositeUOM


class UOMDelegate(QStyledItemDelegate):
    """
    Fixed delegate for UOM selection using a dialog.
    
    Provides UOM selection and handles automatic rate conversion
    when application rate UOMs change.
    """
    
    def __init__(self, parent=None, uom_type="application_rate"):
        """Initialize the UOM delegate."""
        super().__init__(parent)
        self.uom_type = uom_type
        self._uom_list = UOM_CATEGORIES.get(uom_type, [])
    
    def editorEvent(self, event, model, option, index):
        """Handle editor events - open dialog directly on double-click."""
        
        # Check if it's a double-click event
        if (event.type() == QEvent.MouseButtonDblClick and 
            isinstance(event, QMouseEvent)):
            
            # Open dialog directly
            success = self._open_uom_dialog_direct(model, index)
            return success
        
        # Let the base class handle other events
        return super().editorEvent(event, model, option, index)
    
    def displayText(self, value, locale):
        """Format the display text."""
        if value is None or str(value).strip() == "":
            return ""
        return str(value)
    
    def _open_uom_dialog_direct(self, model, index):
        """Open the UOM selection dialog directly and update model."""
        try:
            # Get the table view as parent for proper positioning
            parent = QApplication.activeWindow()
            
            dialog = UOMSelectionDialog(
                parent=parent,
                uom_list=self._uom_list,
                title="Select Application Rate Unit"
            )
            
            # Set current selection if any
            current_uom = index.data(Qt.EditRole) or ""
            
            if current_uom:
                # Pre-select current UOM in dialog if possible
                for i in range(dialog.uom_list.count()):
                    if dialog.uom_list.item(i).text() == current_uom:
                        dialog.uom_list.setCurrentRow(i)
                        break
            
            result = dialog.exec()
            
            if result == QDialog.Accepted:
                selected_uom = dialog.get_selected_uom()
                
                if selected_uom:
                    # Handle rate conversion for application rate UOMs
                    if self.uom_type == "application_rate":
                        success = self._handle_rate_conversion(model, index, selected_uom)
                    else:
                        # For non-rate UOMs, just update directly
                        model.setData(index, selected_uom, Qt.EditRole)
                    return True
            
        except Exception as e:
            print(f"Error in _open_uom_dialog_direct: {e}")
            import traceback
            traceback.print_exc()
        
        return False
    
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