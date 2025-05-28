"""Log calculations and provide a trace of operations."""

from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox, QVBoxLayout
from PySide6.QtGui import QTextCursor, Qt
from common.styles import CALCULATION_TRACE_DIALOG_STYLE, CALCULATION_TRACE_TEXT_AREA_STYLE, CALCULATION_TRACE_BUTTON_STYLE

class CalculationTracer:
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = CalculationTracer()
        return cls._instance
    
    def __init__(self):
        self.messages = []
        self.ui_dialog = None  # Reference to dialog for updates
    
    def log(self, message, end=""):
        self.messages.append(f"{message}{end}")
    
    def clear(self):
        self.messages.clear()
        self._update_ui()
    
    def get_trace(self):
        return "\n".join(self.messages)
    
    def calculation_complete(self):
        self._update_ui()
    
    def _update_ui(self):
        if self.ui_dialog and self.ui_dialog.isVisible():
            self.ui_dialog.update_content()

# Global instance
calculation_tracer = CalculationTracer.get_instance()

class CalculationTraceDialog(QDialog):
    """Dialog to display calculation trace."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculation Trace")
        self.setModal(False)
        self.setWindowState(self.windowState() | Qt.WindowMaximized)
        
        # Import here to avoid circular imports
        self.tracer = calculation_tracer
        
        self.setup_ui()
        self.update_content()
        
        # Register this dialog with the tracer for auto-updates
        self.tracer.ui_dialog = self
    
    def setup_ui(self):
        """Set up the dialog UI."""

        # Apply dialog stylesheet
        self.setStyleSheet(CALCULATION_TRACE_DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        # Text area for trace content
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setStyleSheet(CALCULATION_TRACE_TEXT_AREA_STYLE)
        
        layout.addWidget(self.text_area)
        
        # Button box with Clear and Close buttons
        button_box = QDialogButtonBox()
        button_box.setStyleSheet(CALCULATION_TRACE_BUTTON_STYLE)
        
        # Clear button
        clear_button = button_box.addButton("Clear Terminal", QDialogButtonBox.ActionRole)
        clear_button.clicked.connect(self.clear_trace)
        
        # Close button
        close_button = button_box.addButton("Close", QDialogButtonBox.RejectRole)
        close_button.clicked.connect(self.close)
        
        layout.addWidget(button_box)
    
    def update_content(self):
        """Update the text area with current trace content."""
        trace_content = self.tracer.get_trace()
        if trace_content:
            self.text_area.setPlainText(trace_content)
            # Scroll to bottom to show latest messages
            cursor = self.text_area.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.text_area.setTextCursor(cursor)
        else:
            self.text_area.setPlainText("When calculations are performed, the trace will appear here.")
    
    def clear_trace(self):
        """Clear the calculation trace."""
        self.tracer.clear()
    
    def closeEvent(self, event):
        """Clean up when dialog is closed."""
        if hasattr(self, 'tracer') and self.tracer:
            self.tracer.ui_dialog = None
        
        # Clean up the parent's reference to this dialog
        if self.parent():
            self.parent().trace_dialog = None
        
        event.accept()