"""Applications Table Container for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from season_planner_page.widgets.application_row import ApplicationRowWidget


class ApplicationsTableContainer(QWidget):
    """Container widget for managing multiple application rows in the season planner."""
    
    applications_changed = Signal()  # Signal emitted when any application data changes
    
    def __init__(self, parent=None):
        """Initialize the applications table container."""
        super().__init__(parent)
        self.parent = parent
        self.field_area = 10.0  # Default field area
        self.field_area_uom = "ha"  # Default unit of measure
        self.application_rows = []  # List to track application row widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the table container."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)
        
        # Create header widget with fixed height
        header_widget = QWidget()
        header_widget.setFixedHeight(ApplicationRowWidget.ROW_HEIGHT)
        header_widget.setLayout(header_layout)
        
        # Add header labels
        headers = ["Date", "Type", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        for header_text in headers:
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(label)
        
        # Set stretch factors matching those in ApplicationRowWidget
        stretches = [2, 1, 3, 1, 1, 1, 2, 2, 1]  # Date, Type, Product, Rate, UOM, Area, Method, AIGroups, EIQ
        for i, stretch in enumerate(stretches):
            header_layout.setStretch(i, stretch)
        
        main_layout.addWidget(header_widget)
        
        # Create scroll area for application rows
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container widget for rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(5, 5, 5, 5)
        self.rows_layout.setSpacing(4)
        self.rows_layout.addStretch(1)  # Add stretch to push rows to the top
        
        self.scroll_area.setWidget(self.rows_container)
        main_layout.addWidget(self.scroll_area)
    
    def set_field_area(self, area, uom):
        """Set the default field area for new and existing applications."""
        self.field_area = area
        self.field_area_uom = uom
    
    def add_application_row(self):
        """Add a new application row and return the created widget."""
        row_widget = ApplicationRowWidget(
            parent=self.rows_container, 
            field_area=self.field_area,
            field_area_uom=self.field_area_uom
        )
        
        # Connect signal, add to layout and tracking list
        row_widget.data_changed.connect(self.on_application_data_changed)
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row_widget)
        self.application_rows.append(row_widget)
        
        # Emit signal for the new row
        self.applications_changed.emit()
        return row_widget
    
    def remove_application_row(self, row=None):
        """
        Remove an application row from the container.
        
        Args:
            row: Row widget, index, or None (to remove last row)
            
        Returns:
            bool: True if a row was removed
        """
        # Determine which row widget to remove
        if isinstance(row, int) and 0 <= row < len(self.application_rows):
            row_widget = self.application_rows[row]
        elif row is None and self.application_rows:
            row_widget = self.application_rows[-1]
        else:
            row_widget = row
        
        # Remove the widget if found
        if row_widget in self.application_rows:
            self.application_rows.remove(row_widget)
            self.rows_layout.removeWidget(row_widget)
            row_widget.deleteLater()
            self.applications_changed.emit()
            return True
        
        return False
    
    def on_application_data_changed(self, row_widget):
        """Handle changes to application data in any row."""
        self.applications_changed.emit()
    
    def get_applications(self):
        """Get all applications as a list of dictionaries, excluding empty ones."""
        applications = []
        for row_widget in self.application_rows:
            app_data = row_widget.get_application_data()
            if app_data:  # Only include rows with a product selected
                applications.append(app_data)
        return applications
    
    def set_applications(self, applications):
        """Set the container contents from a list of application dictionaries."""
        self.clear_applications()
        
        for app_data in applications:
            row_widget = self.add_application_row()
            row_widget.set_application_data(app_data)
    
    def clear_applications(self):
        """Clear all application rows from the container."""
        while self.application_rows:
            self.remove_application_row(0)  # Remove first row each time
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return sum(row.get_field_eiq() for row in self.application_rows)
    
    def count(self):
        """Get the number of application rows."""
        return len(self.application_rows)