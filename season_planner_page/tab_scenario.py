"""Scenario Tab for the Season Planner."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PySide6.QtCore import Signal

from common import ContentFrame, get_margin_large, get_spacing_medium, get_subtitle_font
from season_planner_page.widgets.metadata_widget import SeasonPlanMetadataWidget
from season_planner_page.widgets.applications_table import ApplicationsTableWidget
from season_planner_page.models.application_table_model import ValidationState
from data import Scenario, ProductRepository, Application


class ScenarioTabPage(QWidget):
    """
    Tab page for displaying and editing a single scenario.
    
    Provides Excel-like editing capabilities with clean, simple interface.
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
        
        # Set up UI first, then load data, THEN connect signals
        self.setup_ui()
        self.load_scenario_data()
        self.connect_signals()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            get_margin_large(), get_margin_large(), 
            get_margin_large(), get_margin_large()
        )
        main_layout.setSpacing(get_spacing_medium())
        
        # Scenario Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()

        # Simple applications header
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
        try:
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
            
            # Set field area for new applications BEFORE loading applications
            self.applications_table.set_field_area(
                self.scenario.field_area or 0,
                self.scenario.field_area_uom or "acre"
            )
            
            # Update applications table - ensure we're passing Application objects
            if self.scenario.applications and len(self.scenario.applications) > 0:
                applications = []
                for i, app in enumerate(self.scenario.applications):
                    if hasattr(app, 'to_dict'):
                        # It's already an Application object
                        applications.append(app)
                        print(f"  Tab App {i+1}: {app.product_name} @ {getattr(app, 'rate', 'N/A')} {getattr(app, 'rate_uom', 'N/A')}")
                    else:
                        # It might be a dict, convert to Application
                        app_obj = Application.from_dict(app)
                        applications.append(app_obj)
                        print(f"  Tab App {i+1} (converted): {app_obj.product_name} @ {app_obj.rate} {app_obj.rate_uom}")
                
                self.applications_table.set_applications(applications)
            else:
                # No applications - start with empty table
                self.applications_table.clear_applications()
                
        except Exception as e:
            print(f"ERROR in load_scenario_data(): {e}")
            import traceback
            traceback.print_exc()
    
    def update_scenario(self):
        """Update scenario with current UI data and emit change signal."""
        try:
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
            
        except Exception as e:
            print(f"ERROR in update_scenario(): {e}")
            import traceback
            traceback.print_exc()
    
    def _on_eiq_changed(self, total_eiq):
        """Handle EIQ changes from the applications table."""
        # This can be used for real-time EIQ updates in the parent
        # The parent scenarios manager will update its display automatically
        # when scenario_changed is emitted
        pass
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return self.applications_table.get_total_field_eiq()
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        try:
            self.applications_table.refresh_product_data()
        except Exception as e:
            print(f"ERROR in refresh_product_data(): {e}")
    
    def get_scenario(self):
        """Get the current scenario object."""
        return self.scenario
    
    def get_validation_summary(self):
        """Get validation summary for this scenario."""
        try:
            return self.applications_table.model.get_validation_summary()
        except Exception as e:
            print(f"ERROR in get_validation_summary(): {e}")
            return {}
    
    def has_validation_issues(self) -> bool:
        """Check if this scenario has any validation issues."""
        try:
            summary = self.get_validation_summary()
            
            issue_count = (
                summary.get(ValidationState.INVALID_PRODUCT, 0) +
                summary.get(ValidationState.INVALID_DATA, 0) +
                summary.get(ValidationState.INCOMPLETE, 0)
            )
            
            return issue_count > 0
            
        except Exception as e:
            print(f"ERROR in has_validation_issues(): {e}")
            return False
    
    def get_applications_count(self) -> int:
        """Get the number of applications in this scenario."""
        try:
            return len(self.scenario.applications) if self.scenario.applications else 0
        except Exception:
            return 0