"""Log calculations and provide a trace of operations."""

from PySide6.QtWidgets import QDialog, QTextEdit, QDialogButtonBox
from PySide6.QtGui import QTextCursor

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
    
    def log(self, message):
        self.messages.append(message)
    
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
        self.setModal(True)
        self.resize(800, 600)
        
        # Import here to avoid circular imports
        from common.tracer import calculation_tracer
        self.tracer = calculation_tracer
        
        self.setup_ui()
        self.update_content()
        
        # Register this dialog with the tracer for auto-updates
        self.tracer.ui_dialog = self
    
    def setup_ui(self):
        """Set up the dialog UI."""
        from PySide6.QtWidgets import QVBoxLayout
        from PySide6.QtGui import QFont
        
        layout = QVBoxLayout(self)
        
        # Text area for trace content
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        
        # Use monospace font for better formatting
        mono_font = QFont("Courier New", 9)
        self.text_area.setFont(mono_font)
        
        layout.addWidget(self.text_area)
        
        # Button box with Clear and Close buttons
        button_box = QDialogButtonBox()
        
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
            self.text_area.setPlainText("No calculation trace available yet.\n\nPerform an EIQ calculation to see the trace here.")
    
    def clear_trace(self):
        """Clear the calculation trace."""
        self.tracer.clear()
    
    def closeEvent(self, event):
        """Clean up when dialog is closed."""
        self.tracer.ui_dialog = None
        event.accept()