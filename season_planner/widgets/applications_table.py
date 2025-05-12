"""
Applications Table Container for the LORENZO POZZI Pesticide App.

This module defines a custom container widget for managing multiple
application rows in the season planner.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame,
                             QLabel, QHeaderView, QSizePolicy, QHBoxLayout)
from PySide6.QtCore import Qt, Signal
from season_planner.widgets.application_row import ApplicationRowWidget


class ApplicationsTableContainer(QWidget):
    """
    Container widget for managing multiple application rows.
    
    This widget acts as a container for ApplicationRowWidget instances,
    managing their addition, removal, and overall layout.
    """
    
    # Signal emitted when any application data changes
    applications_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the applications table container."""
        super().__init__(parent)
        self.parent = parent
        self.field_area = 10.0  # Default field area
        self.field_area_uom = "ha"  # Default unit of measure
        self.application_rows = []  # List to track application row widgets
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)
        
        # Add header labels with matching widths and alignments to the application rows
        headers = ["Date", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        for idx, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(label)
        
        # Set stretch factors matching those in ApplicationRowWidget
        header_layout.setStretch(0, 2)  # Date
        header_layout.setStretch(1, 3)  # Product
        header_layout.setStretch(2, 1)  # Rate
        header_layout.setStretch(3, 1)  # UOM
        header_layout.setStretch(4, 1)  # Area
        header_layout.setStretch(5, 2)  # Method
        header_layout.setStretch(6, 2)  # AI Groups
        header_layout.setStretch(7, 1)  # Field EIQ
        
        header_widget = QWidget()
        header_widget.setLayout(header_layout)
        main_layout.addWidget(header_widget)
        
        # Create scroll area for application rows
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container widget for rows
        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(2)  # Small spacing between rows
        self.rows_layout.addStretch(1)  # Add stretch at the end to push rows to the top
        
        scroll_area.setWidget(self.rows_container)
        main_layout.addWidget(scroll_area)
    
    def set_field_area(self, area, uom):
        """
        Set the default field area for new and existing applications.
        
        Args:
            area (float): Area value
            uom (str): Unit of measure
        """
        self.field_area = area
        self.field_area_uom = uom
        
        # Update field area in all existing application rows
        for row in self.application_rows:
            row.set_field_area(area, uom)
    
    def add_application_row(self):
        """
        Add a new application row to the container.
        
        Returns:
            ApplicationRowWidget: The newly created row widget
        """
        # Create new row widget
        row_widget = ApplicationRowWidget(
            parent=self, 
            field_area=self.field_area,
            field_area_uom=self.field_area_uom
        )
        
        # Connect data changed signal
        row_widget.data_changed.connect(self.on_application_data_changed)
        
        # Add widget to layout before the stretch
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row_widget)
        
        # Add to tracking list
        self.application_rows.append(row_widget)
        
        # Emit signal for the new row
        self.applications_changed.emit()
        
        return row_widget
    
    def remove_application_row(self, row=None):
        """
        Remove an application row from the container.
        
        Args:
            row: The row widget to remove or index.
                If None, attempts to find a selected row.
        
        Returns:
            bool: True if a row was removed, False otherwise
        """
        # If row is an integer index, get the widget
        if isinstance(row, int) and 0 <= row < len(self.application_rows):
            row_widget = self.application_rows[row]
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
        """
        Handle changes to application data in any row.
        
        Args:
            row_widget: The row widget that changed
        """
        # Emit signal for data change
        self.applications_changed.emit()
    
    def get_applications(self):
        """
        Get all applications from the container as a list of dictionaries.
        
        Returns:
            list: List of application dictionaries
        """
        applications = []
        
        for row_widget in self.application_rows:
            app_data = row_widget.get_application_data()
            if app_data:  # Only include rows with a product selected
                applications.append(app_data)
        
        return applications
    
    def set_applications(self, applications):
        """
        Set the container contents from a list of application dictionaries.
        
        Args:
            applications (list): List of application dictionaries
        """
        # Clear existing applications
        self.clear_applications()
        
        # Add each application
        for app_data in applications:
            row_widget = self.add_application_row()
            row_widget.set_application_data(app_data)
    
    def clear_applications(self):
        """Clear all application rows from the container."""
        # Remove all application rows
        while self.application_rows:
            self.remove_application_row(self.application_rows[0])
    
    def get_total_field_eiq(self):
        """
        Calculate the total Field EIQ for all applications.
        
        Returns:
            float: Total Field EIQ
        """
        return sum(row.get_field_eiq() for row in self.application_rows)
    
    def count(self):
        """
        Get the number of application rows.
        
        Returns:
            int: Number of application rows
        """
        return len(self.application_rows)