"""
Fixed calculation tracer with clean, readable output structure.
Key changes: simplified tree structure, eliminated redundancy, clear visual hierarchy.

Usage in layer_1_interface.py:
- Replace detailed substep chains with log_conversion_simple()
- Use log_calculation_formula() for math operations
- Set suppress_redundant flag during unit standardization

Usage in layer_2_uom_std.py:
- Simplify conversion logging to one line per conversion
- Remove excessive nesting and duplicate logs

Usage in layer_3_eiq_math.py:
- Use log_calculation_formula() for clean formula display
"""

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
        self.ui_dialog = None
        self._current_step = 0
        self._suppress_redundant = False  # Flag to prevent duplicate logging
        
    def log_header(self, title):
        """Log a major calculation header."""
        separator = "=" * 60
        self.messages.append(separator)
        self.messages.append(f"  {title.upper()}")
        self.messages.append(separator)
        self.messages.append("")
        self._current_step = 0
    
    def log_step(self, description):
        """Log a major calculation step with clear separation."""
        self._current_step += 1
        if self._current_step > 1:
            self.messages.append("")  # Add spacing between steps
        self.messages.append(f"{self._current_step}: {description}")
        self.messages.append("─" * 40)
    
    def log_substep(self, description, level=1, is_last=False):
        """Log a substep with clean tree structure - avoid redundant calls."""
        if self._suppress_redundant and level > 2:
            return  # Skip overly nested redundant logs
            
        if level == 1:
            prefix = "  •"
        elif level == 2:
            prefix = "    └─"
        else:
            prefix = "      " + ("└─" if is_last else "├─")
        
        self.messages.append(f"{prefix} {description}")
    
    def log_conversion_simple(self, description, from_val, from_unit, to_val, to_unit):
        """Log a simple conversion in one clean line."""
        if from_val == to_val and from_unit == to_unit:
            self.messages.append(f"  • {description}: {from_val} {from_unit} (no conversion needed)")
        else:
            self.messages.append(f"  • {description}: {from_val} {from_unit} → {to_val} {to_unit}")
    
    def log_ai_list(self, ai_data, level=1):
        """Log active ingredients in compact format."""
        if not ai_data:
            self.log_substep("No active ingredients found", level)
            return
            
        self.messages.append(f"  • Active Ingredients ({len(ai_data)}):")
        for ai in ai_data:
            eiq_text = f"EIQ: {ai['eiq']}" if ai.get('eiq') not in [None, "--"] else "EIQ: --"
            conc_text = f"{ai['concentration']} {ai['uom']}" if ai.get('concentration') not in [None, "--"] else "--"
            self.messages.append(f"    └─ {ai['name']}: {conc_text}, {eiq_text}")
    
    def log_application_info(self, rate, unit, applications, level=1):
        """Log application info in one clean line."""
        app_text = f"{applications} application" + ("s" if applications != 1 else "")
        self.messages.append(f"  • Application Rate: {rate} {unit} × {app_text}")
    
    def log_result(self, description, value, unit=None, level=0):
        """Log final result with emphasis."""
        unit_str = f" {unit}" if unit else ""
        if level == 0:
            self.messages.append("")
            self.messages.append("─" * 40)
            self.messages.append(f"RESULT: {value}{unit_str}")
            self.messages.append("=" * 60)
        else:
            self.messages.append(f"  • {description}: {value}{unit_str}")
    
    def log_calculation_formula(self, ai_name, rate, concentration, eiq, applications, result):
        """Log calculation formula in clean, readable format."""
        self.messages.append(f"  • {ai_name}:")
        self.messages.append(f"    └─ {rate} × {concentration} × {eiq} × {applications} = {result} eiq/ha")
    
    def log_total_calculation(self, breakdown, total):
        """Log total calculation when multiple AIs."""
        if len(breakdown) > 1:
            parts = " + ".join([f"{eiq:.1f}" for eiq in breakdown.values()])
            self.messages.append(f"  • Total: {parts} = {total:.1f} eiq/ha")
    
    def set_suppress_redundant(self, suppress=True):
        """Control whether to suppress redundant detailed logging."""
        self._suppress_redundant = suppress
    
    def add_blank_line(self):
        """Add spacing."""
        self.messages.append("")
    
    def log(self, message, end=""):
        """Legacy compatibility."""
        self.messages.append(f"{message}{end}")
    
    def clear(self):
        self.messages.clear()
        self._current_step = 0
        self._suppress_redundant = False
        self._update_ui()
    
    def get_trace(self):
        return "\n".join(self.messages)
    
    def calculation_complete(self):
        self._update_ui()
    
    def _update_ui(self):
        if self.ui_dialog and self.ui_dialog.isVisible():
            self.ui_dialog.update_content()

    def log_separator(self, char="─", length=40):
        """Add visual separator."""
        self.messages.append(char * length)

# Global instance
calculation_tracer = CalculationTracer.get_instance()

class CalculationTraceDialog(QDialog):
    """Dialog to display calculation trace."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Calculation Trace")
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