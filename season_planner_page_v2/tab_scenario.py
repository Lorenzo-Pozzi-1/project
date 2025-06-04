"""
Scenario Tab for Season Planner V2.

Individual scenario tab using the new table-based applications interface.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal

from common import create_button, ContentFrame, get_margin_large, get_spacing_medium, get_subtitle_font
from season_planner_page_v2.widgets.metadata_widget import SeasonPlanMetadataWidget
from season_planner_page_v2.widgets.applications_table import ApplicationsTableWidget
from data import Scenario, Application, ProductRepository


class ScenarioTabPage(QWidget):
    """
    Tab page for displaying and editing a single scenario using the new table interface.
    
    This replaces the old widget-based approach with a clean table view that provides
    Excel-like editing capabilities.
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
        self.connect_signals()
        self.load_scenario_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Scenario Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        applications_layout.addWidget(QLabel("Applications", font=get_subtitle_font()))
        
        # Applications Table Widget
        self.applications_table = ApplicationsTableWidget()
        applications_layout.addWidget(self.applications_table)
        
        applications_frame.layout.addLayout(applications_layout)
        main_layout.addWidget(applications_frame)
    
    def connect_signals(self):
        """Connect widget signals to update handlers."""
        # Metadata changes
        self.metadata_widget.metadata_changed.connect(self.update_scenario)
        
        # Applications changes
        self.applications_table.applications_changed.connect(self.update_scenario)
        self.applications_table.eiq_changed.connect(self._on_eiq_changed)
    
    def load_scenario_data(self):
        """Populate the UI with data from the current scenario object."""
        # Update metadata widget
        metadata = {
            "crop_year": self.scenario.crop_year,
            "grower_name": self.scenario.grower_name or "",
            "field_name": self.scenario.field_name or "",
            "field_area": self.scenario.field_area or 0,
            "field_area_uom": self.scenario.field_area_uom or "acre",
            "variety": self.scenario.variety or ""
        }
        self.metadata_widget.set_metadata(metadata)
        
        # Update applications table
        self.applications_table.set_applications(self.scenario.applications)
        
        # Set field area for new applications
        self.applications_table.set_field_area(
            self.scenario.field_area or 0,
            self.scenario.field_area_uom or "acre"
        )
    
    def update_scenario(self):
        """Update scenario with current UI data and emit change signal."""
        # Update metadata
        metadata = self.metadata_widget.get_metadata()
        for key, value in metadata.items():
            setattr(self.scenario, key, value)
        
        # Update field area in applications table
        self.applications_table.set_field_area(
            metadata["field_area"], 
            metadata["field_area_uom"]
        )
        
        # Update applications
        self.scenario.applications = self.applications_table.get_applications()
        
        # Emit signal
        self.scenario_changed.emit(self.scenario)
    
    def _on_eiq_changed(self, total_eiq):
        """Handle EIQ changes from the applications table."""
        # This can be used for real-time EIQ updates in the parent
        pass
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return self.applications_table.get_total_field_eiq()
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        self.applications_table.refresh_product_data()
    
    def get_scenario(self):
        """Get the current scenario object."""
        # Ensure scenario is up to date before returning
        self.update_scenario()
        return self.scenario