"""
Scenario tab for the LORENZO POZZI Pesticide App.

This module provides a tab for viewing and editing the individual scenarios.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal
from common import create_button, ContentFrame, get_config, eiq_calculator, get_margin_large, get_spacing_medium, get_subtitle_font
from season_planner_page.widget_metadata_row import SeasonPlanMetadataWidget
from season_planner_page.widget_applications_table import ApplicationsTableContainer
from data import Scenario, Application, ProductRepository

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
        self.products_repo = ProductRepository.get_instance()    
        self.setup_ui()
        self.load_scenario_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Scenario Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        self.metadata_widget.metadata_changed.connect(self.update_scenario)
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        applications_layout.addWidget(QLabel("Applications", font=get_subtitle_font()))
        
        # Applications Table Container
        self.applications_container = ApplicationsTableContainer()
        self.applications_container.applications_changed.connect(self.update_scenario)
        applications_layout.addWidget(self.applications_container)
        
        # Add application button
        buttons_layout = QHBoxLayout()
        add_button = create_button(text="Add Application", style="white", callback=self.applications_container.add_application_row, parent=self)
        buttons_layout.addWidget(add_button)
        buttons_layout.addStretch(1)
        applications_layout.addLayout(buttons_layout)
        applications_frame.layout.addLayout(applications_layout)
        main_layout.addWidget(applications_frame)
    
    def load_scenario_data(self):
        """Populate the UI with data from the current scenario object."""
        
        # Convert application objects to dictionaries for the table widget
        app_dicts = [app.to_dict() for app in self.scenario.applications]

        # Update the metadata widget with the scenario's values with safe defaults
        metadata = {
            "crop_year": self.scenario.crop_year,
            "grower_name": self.scenario.grower_name or "",
            "field_name": self.scenario.field_name or "",
            "field_area": self.scenario.field_area or 0,
            "field_area_uom": self.scenario.field_area_uom or "acre",
            "variety": self.scenario.variety or ""
        }
        self.metadata_widget.set_metadata(metadata)

        # Populate the applications table with the scenario's application data
        self.applications_container.set_applications(app_dicts)
        
    def update_scenario(self):
        """Update scenario with current UI data and emit change signal."""
        # Update metadata
        metadata = self.metadata_widget.get_metadata()
        for key, value in metadata.items():
            setattr(self.scenario, key, value)
            
        # Update field area in applications container
        self.applications_container.set_field_area(metadata["field_area"], metadata["field_area_uom"])
        
        # Update applications
        self.scenario.applications = [
            Application.from_dict(app_data) 
            for app_data in self.applications_container.get_applications()
        ]
        
        # Emit signal
        self.scenario_changed.emit(self.scenario)
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        try:
            # Get user preferences for UOM conversions
            user_preferences = get_config("user_preferences", {})
            
            # Get all applications data
            applications_data = self.applications_container.get_applications()
            
            # Use the scenario-level calculation
            total_eiq = eiq_calculator.calculate_scenario_field_eiq(
                applications=[{
                    'product': self.products_repo.get_product_by_name(app.get('product_name')),
                    'rate': app.get('rate', 0),
                    'rate_uom': app.get('rate_uom', ''),
                } for app in applications_data if app.get('product_name')],
                user_preferences=user_preferences
            )
            
            return total_eiq
            
        except Exception as e:
            print(f"Error calculating total scenario EIQ: {e}")
            return 0.0
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        self.applications_container.set_applications(self.applications_container.get_applications())
        
    def get_scenario(self):
        """Get the current scenario object."""
        return self.scenario