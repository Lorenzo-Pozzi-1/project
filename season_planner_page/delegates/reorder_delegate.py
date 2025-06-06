"""
Reorder Delegate for the Season Planner Applications Table.

Provides up/down arrow buttons to reorder application rows.
"""

from PySide6.QtWidgets import QStyledItemDelegate, QWidget, QHBoxLayout, QPushButton, QStyle
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette


class ReorderButtonWidget(QWidget):
    """Widget containing up/down buttons for reordering."""
    
    move_up = Signal(int)  # Emitted with row index
    move_down = Signal(int)  # Emitted with row index
    
    def __init__(self, row: int, parent=None):
        super().__init__(parent)
        self.row = row
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the button layout."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(1)
        
        # Up button
        self.up_button = QPushButton("▲")
        self.up_button.setMaximumSize(20, 20)
        self.up_button.setMinimumSize(20, 20)
        self.up_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #ccc;
            }
        """)
        self.up_button.clicked.connect(lambda: self.move_up.emit(self.row))
        layout.addWidget(self.up_button)
        
        # Down button
        self.down_button = QPushButton("▼")
        self.down_button.setMaximumSize(20, 20)
        self.down_button.setMinimumSize(20, 20)
        self.down_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
            QPushButton:disabled {
                background-color: #f8f8f8;
                color: #ccc;
            }
        """)
        self.down_button.clicked.connect(lambda: self.move_down.emit(self.row))
        layout.addWidget(self.down_button)
    
    def update_buttons(self, is_first: bool, is_last: bool):
        """Update button enabled state based on position."""
        self.up_button.setEnabled(not is_first)
        self.down_button.setEnabled(not is_last)


class ReorderDelegate(QStyledItemDelegate):
    """
    Custom delegate for reorder column that shows up/down buttons.
    """
    
    move_up = Signal(int)  # Emitted with row index
    move_down = Signal(int)  # Emitted with row index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._button_widgets = {}  # Cache button widgets by row
    
    def createEditor(self, parent, option, index):
        """Create the editor widget (button container)."""
        if not index.isValid():
            return None
        
        row = index.row()
        widget = ReorderButtonWidget(row, parent)
        
        # Connect signals
        widget.move_up.connect(self.move_up)
        widget.move_down.connect(self.move_down)
        
        # Update button states
        model = index.model()
        if model:
            row_count = model.rowCount()
            is_first = (row == 0)
            is_last = (row == row_count - 1)
            widget.update_buttons(is_first, is_last)
        
        return widget
    
    def updateEditorGeometry(self, editor, option, index):
        """Update the editor geometry to match the cell."""
        if editor:
            editor.setGeometry(option.rect)
    
    def setEditorData(self, editor, index):
        """Set editor data - not needed for buttons."""
        pass
    
    def setModelData(self, editor, model, index):
        """Set model data - not needed for buttons."""
        pass
    
    def paint(self, painter, option, index):
        """Paint the cell - just show placeholder text."""
        painter.save()
          # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, option.palette.highlight())
        else:
            painter.fillRect(option.rect, option.palette.base())
        
        # Draw centered text indicating this is the reorder column
        painter.setPen(option.palette.color(QPalette.Text))
        painter.drawText(option.rect, Qt.AlignCenter, "↕")
        
        painter.restore()
    
    def sizeHint(self, option, index):
        """Return size hint for the reorder column."""
        size = super().sizeHint(option, index)
        size.setWidth(50)  # Fixed width for reorder column
        return size
