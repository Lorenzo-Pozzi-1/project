"""
Group Divider Delegate for STIR Operations Table.

Draws horizontal divider lines between different operation groups.
"""

from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPen, QColor


class GroupDividerDelegate(QStyledItemDelegate):
    """Custom delegate that draws horizontal divider lines between groups."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def paint(self, painter, option, index):
        """Paint the item with a horizontal divider line if it's a group boundary."""
        # First, paint the normal item
        super().paint(painter, option, index)
        
        # Check if this row needs a divider line above it
        model = index.model()
        if hasattr(model, 'is_group_boundary') and model.is_group_boundary(index.row()):
            # Draw a horizontal line at the top of this cell
            painter.save()
            
            # Set up the pen for the divider line
            pen = QPen(Qt.black, 5, Qt.SolidLine)
            painter.setPen(pen)
            
            # Draw the line across the full width of the cell
            line_y = option.rect.top()
            painter.drawLine(
                option.rect.left(), 
                line_y, 
                option.rect.right(), 
                line_y
            )
            
            painter.restore()
