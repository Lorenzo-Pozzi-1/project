"""
Scenario tab page for the LORENZO POZZI Pesticide App.

This module provides a tab page for viewing and editing a single scenario.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Signal
from datetime import date
from common.styles import MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, get_title_font
from common.widgets import ContentFrame
from season_planner_page.widgets import SeasonPlanMetadataWidget, ApplicationsTableContainer
from data.scenario_model import Scenario

class ScenarioTabPage(QWidget):
    """
    Tab page for displaying and editing a single scenario.
    
    This is a modified version of SeasonPlannerPage designed to work
    within the scenarios tab interface.
    """
    
    scenario_changed = Signal(object)  # Emitted when scenario data changes
    
    def __init__(self, parent=None, scenario=None):
        """
        Initialize the scenario tab page.
        
        Args:
            parent: Parent widget
            scenario: Scenario object to edit, creates a new one if None
        """
        super().__init__(parent)
        self.parent = parent
        self.scenario = scenario or Scenario()
        self.setup_ui()
        self.load_scenario_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Scenario Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        self.metadata_widget.metadata_changed.connect(self.on_metadata_changed)
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Applications")
        title_label.setFont(get_title_font(size=16))
        applications_layout.addWidget(title_label)
        
        # Applications Table Container
        self.applications_container = ApplicationsTableContainer()
        self.applications_container.applications_changed.connect(self.on_applications_changed)
        applications_layout.addWidget(self.applications_container)
        
        # Button to add new application (moved from the original)
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Application")
        add_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_button.clicked.connect(self.add_application)
        buttons_layout.addWidget(add_button)
        buttons_layout.addStretch(1)
        
        applications_layout.addLayout(buttons_layout)
        applications_frame.layout.addLayout(applications_layout)
        main_layout.addWidget(applications_frame)
    
    def load_scenario_data(self):
        """Load data from the scenario into the UI."""
        if not self.scenario:
            return
            
        # Set metadata with safe defaults
        metadata = {
            "crop_year": self.scenario.crop_year,
            "grower_name": self.scenario.grower_name or "",
            "field_name": self.scenario.field_name or "",
            "field_area": 10.0 if self.scenario.field_area is None else self.scenario.field_area,
            "field_area_uom": self.scenario.field_area_uom or "ha",
            "variety": self.scenario.variety or ""
        }
        self.metadata_widget.set_metadata(metadata)
        
        # Set applications
        self.applications_container.set_applications(
            [app.to_dict() for app in self.scenario.applications]
        )
    
    def on_metadata_changed(self):
        """Handle changes to scenario metadata."""
        if not self.scenario:
            return
            
        metadata = self.metadata_widget.get_metadata()
        
        # Update scenario with new metadata
        self.scenario.crop_year = metadata["crop_year"]
        self.scenario.grower_name = metadata["grower_name"]
        self.scenario.field_name = metadata["field_name"]
        self.scenario.field_area = metadata["field_area"]
        self.scenario.field_area_uom = metadata["field_area_uom"]
        self.scenario.variety = metadata["variety"]
        
        # Update field area in applications container
        self.applications_container.set_field_area(
            metadata["field_area"], 
            metadata["field_area_uom"]
        )
        
        # Emit signal
        self.scenario_changed.emit(self.scenario)
    
    def on_applications_changed(self):
        """Handle changes to applications."""
        if not self.scenario:
            return
            
        # Get applications from container
        applications = self.applications_container.get_applications()
        
        # Update scenario with applications
        from data.application_model import Application
        self.scenario.applications = [
            Application.from_dict(app_data) for app_data in applications
        ]
        
        # Emit signal
        self.scenario_changed.emit(self.scenario)
    
    def add_application(self):
        """Add a new application row to the container."""
        self.applications_container.add_application_row()
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return self.applications_container.get_total_field_eiq()
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        applications = self.applications_container.get_applications()
        self.applications_container.set_applications(applications)
        
    def get_scenario(self):
        """Get the current scenario object."""
        return self.scenario