"""Applications Table Container for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QColor
from common import ContentFrame, GENERIC_TABLE_STYLE, WHITE, ALTERNATE_ROW_COLOR, get_config
from season_planner_page.widget_application_row import ApplicationRowWidget


class ApplicationsTableContainer(QWidget):
    """Container widget for managing multiple application rows."""
    
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
        
        # Wrap header in ContentFrame
        header_frame = ContentFrame()
        header_layout = QVBoxLayout()
        
        # Header row
        header_row_layout = QHBoxLayout()
        header_row_layout.setContentsMargins(2, 1, 2, 1)
        header_row_layout.setSpacing(5)
        
        # Define headers and their stretch factors
        headers = ["Product No", "Date", "Type", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        stretches = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        
        # Create and add header labels
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("font-weight: bold;")
            header_row_layout.addWidget(label)
            header_row_layout.setStretch(i, stretches[i])
        
        # Extra column for delete button
        header_row_layout.addWidget(QLabel(""))
        header_row_layout.setStretch(len(headers), 0)
        
        header_layout.addLayout(header_row_layout)
        header_frame.layout.addLayout(header_layout)
        
        # Apply the comparison header style
        header_frame.setStyleSheet(GENERIC_TABLE_STYLE)
        header_frame.setFixedHeight(ApplicationRowWidget.ROW_HEIGHT)
        
        main_layout.addWidget(header_frame)
        
        # Wrap scroll area in ContentFrame
        content_frame = ContentFrame()
        content_layout = QVBoxLayout()
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container for rows
        self.rows_container = QWidget()
        self.rows_container.setObjectName("rowsContainer")
        
        # Create layout for rows
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(5, 5, 5, 5)
        self.rows_layout.setSpacing(1)
        self.rows_layout.addStretch(1)  # Push rows to the top
        
        # Set up the scroll area
        self.scroll_area.setWidget(self.rows_container)
        content_layout.addWidget(self.scroll_area)
        
        content_frame.layout.addLayout(content_layout)
        main_layout.addWidget(content_frame)
    
    def add_application_row(self):
        """Add a new application row and return the created widget."""
        index = len(self.application_rows)
        row_widget = ApplicationRowWidget(
            parent=self.rows_container, 
            field_area=self.field_area,
            field_area_uom=self.field_area_uom,
            index=index
        )

        # Connect signals
        row_widget.data_changed.connect(self.on_application_data_changed)
        row_widget.delete_requested.connect(self.remove_application_row)
        
        # Add to layout and tracking list
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row_widget)
        self.application_rows.append(row_widget)
        
        # Update row number
        row_widget.update_app_number(index + 1)

        # Update row colors after adding new row
        self.update_row_colors()

        # Emit signal for the new row
        self.applications_changed.emit()
        return row_widget
    
    def update_row_colors(self):
        """Apply alternating background colors to all rows."""
        for i, row in enumerate(self.application_rows):
            palette = row.palette()
            if i % 2 == 1:  # Odd rows
                palette.setColor(QPalette.Window, QColor(ALTERNATE_ROW_COLOR))
            else:  # Even rows
                palette.setColor(QPalette.Window, QColor(WHITE))
            row.setPalette(palette)
            row.setAutoFillBackground(True)
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        try:
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Collect all application EIQ values
            total_eiq = 0.0
            for row in self.application_rows:
                app_data = row.get_application_data()
                if app_data and app_data.get('product_name'):
                    # Use the individual row's calculated EIQ
                    row_eiq = row.get_field_eiq()
                    total_eiq += row_eiq
            
            return total_eiq
            
        except Exception as e:
            print(f"Error calculating total Field EIQ: {e}")
            return 0.0
    
    def get_applications(self):
        """Get all applications as a list of dictionaries, excluding empty ones."""
        return [app_data for row_widget in self.application_rows 
                if (app_data := row_widget.get_application_data())]

    def set_applications(self, applications):
        """Set the container contents from a list of application dictionaries."""
        self.clear_applications()
        
        for app_data in applications:
            row_widget = self.add_application_row()
            row_widget.set_application_data(app_data)
        
        # Make sure colors are correctly applied after loading applications
        self.update_row_colors()

    def clear_applications(self):
        """Clear all application rows from the container."""
        while self.application_rows:
            self.remove_application_row(self.application_rows[0])

    def set_field_area(self, area, uom):
        """Set the default field area for new applications."""
        self.field_area = area
        self.field_area_uom = uom

    def on_application_data_changed(self, row_widget):
        """Handle changes to application data in any row."""
        self.applications_changed.emit()
    
    def update_row_indices(self):
        """Update the indices of all rows after reordering."""
        for i, row in enumerate(self.application_rows):
            row.set_index(i)
            row.update_app_number(i + 1)
        
        # Update row colors whenever indices are updated
        self.update_row_colors()
    
    def remove_application_row(self, row):
        """Remove an application row from the container."""
        if row not in self.application_rows:
            return False
            
        # Remove from list and layout
        self.application_rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()
        
        # Update indices
        self.update_row_indices()
        self.applications_changed.emit()
        return True
    
    def update_default_field_area(self, area, uom):
        """
        Update the default field area for new applications without changing existing rows.
        """
        self.field_area = area
        self.field_area_uom = uom