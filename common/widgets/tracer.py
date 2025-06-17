"""calculation tracer for production-ready logging."""

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
        self._indent_level = 0
        self._current_step = 0
        
    def log_header(self, title):
        """Log a major calculation header."""
        separator = "=" * (len(title) + 8)
        self.messages.append(separator)
        self.messages.append(f"=== {title.upper()} ===")
        self.messages.append(separator)
        self.messages.append("")
        self._current_step = 0
    
    def log_step(self, description):
        """Log a major calculation step."""
        self._current_step += 1
        self.messages.append(f"STEP {self._current_step}: {description}")
        self._indent_level = 0
    
    def log_substep(self, description, level=1, is_last=False):
        """Log a substep with appropriate tree characters."""
        prefix = self._get_tree_prefix(level, is_last)
        self.messages.append(f"{prefix} {description}")
    
    def log_formula(self, formula, substitution, result, level=1, is_last=False):
        """Log a formula with substitution and result."""
        prefix = self._get_tree_prefix(level, is_last)
        self.messages.append(f"{prefix} {formula}")
        if substitution != formula:
            sub_prefix = self._get_tree_prefix(level + 1, True)
            self.messages.append(f"{sub_prefix} {substitution} = {result}")
    
    def log_conversion(self, value, from_unit, to_unit, result, level=1, is_last=False):
        """Log a unit conversion."""
        prefix = self._get_tree_prefix(level, is_last)
        if result == value:
            self.messages.append(f"{prefix} {value} {from_unit} → {result} {to_unit} ✓")
        else:
            self.messages.append(f"{prefix} {value} {from_unit} → {result} {to_unit}")
    
    def log_result(self, description, value, unit=None, level=0):
        """Log a final result."""
        if level == 0:
            self.messages.append("")
            unit_str = f" {unit}" if unit else ""
            self.messages.append(f"RESULT: {value}{unit_str}")
        else:
            prefix = self._get_tree_prefix(level, True)
            unit_str = f" {unit}" if unit else ""
            self.messages.append(f"{prefix} {description}: {value}{unit_str}")
    
    def log_ai_list(self, ai_data, level=1):
        """Log a list of active ingredients."""
        if not ai_data:
            self.log_substep("No active ingredients found", level, True)
            return
            
        self.log_substep(f"Active Ingredients: {len(ai_data)} found", level)
        for i, ai in enumerate(ai_data):
            is_last = (i == len(ai_data) - 1)
            eiq_text = f"EIQ: {ai['eiq']}" if ai.get('eiq') is not None else "EIQ: --"
            conc_text = f"{ai['concentration']} {ai['uom']}" if ai.get('concentration') is not None else "--"
            self.log_substep(f"{ai['name']}: {conc_text} ({eiq_text})", level + 1, is_last)
    
    def log_application_info(self, rate, unit, applications, level=1):
        """Log application rate and count information."""
        app_text = f"{applications} application" + ("s" if applications != 1 else "")
        self.log_substep(f"Application: {rate} {unit} × {app_text}", level, True)
    
    def _get_tree_prefix(self, level, is_last=False):
        """Generate tree-style prefix based on indentation level."""
        if level == 0:
            return ""
        elif level == 1:
            return "└─" if is_last else "├─"
        else:
            base = "│  " * (level - 2)
            if level == 2:
                return f"│  └─" if is_last else f"│  ├─"
            else:
                return f"{base}   └─" if is_last else f"{base}   ├─"
    
    def add_blank_line(self):
        """Add a blank line for spacing."""
        self.messages.append("")
    
    def log(self, message, end=""):
        """Legacy method for backward compatibility."""
        self.messages.append(f"{message}{end}")
    
    def clear(self):
        self.messages.clear()
        self._current_step = 0
        self._indent_level = 0
        self._update_ui()
    
    def get_trace(self):
        return "\n".join(self.messages)
    
    def calculation_complete(self):
        self.add_blank_line()
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
        self.setWindowTitle("Calculation Trace - STILL IN DEVELOPMENT: needs some visual touch-ups")
        self.setModal(False)
        
        # Set window flags to include maximize button and make resizable
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set minimum size
        self.setMinimumSize(1000, 500)
        
        # Start maximized (optional - you can remove this line if you prefer default size)
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