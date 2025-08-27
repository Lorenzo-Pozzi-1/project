"""
Scenarios Comparison Page for the Season Planner.

A container page that displays multiple ScenarioComparisonTable widgets
to compare scenarios side by side.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from common.constants import get_margin_large, get_spacing_medium
from common.styles import get_medium_font
from common.widgets.header_frame_buttons import HeaderWithHomeButton
from common.widgets.scorebar import ScoreBar
from .widgets.scenario_comparison_table import ScenarioComparisonTable


class ScenariosComparisonPage(QWidget):
    """
    Page for comparing scenarios side by side.
    
    Acts as a container for multiple ScenarioComparisonTable widgets.
    """
    
    def __init__(self, parent=None):
        """Initialize the scenarios comparison page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), 
                                     get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with back button
        header = HeaderWithHomeButton("Scenarios Comparison")
        header.back_clicked.connect(self.go_back)
        main_layout.addWidget(header)
        
        # Scroll area for scenario tables
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for scenarios
        self.scenarios_container = QWidget()
        self.scenarios_layout = QHBoxLayout(self.scenarios_container)
        self.scenarios_layout.setSpacing(get_spacing_medium())
        self.scenarios_layout.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidget(self.scenarios_container)
        main_layout.addWidget(scroll_area)
        
        # Add ScoreBar at the bottom for scenarios comparison
        self.score_bar = ScoreBar(preset="regen_ag")
        main_layout.addWidget(self.score_bar)
    
    def showEvent(self, event):
        """Called when the page is shown. Load scenarios here."""
        super().showEvent(event)
        self.load_scenarios()
    
    def load_scenarios(self):
        """Load scenarios from the parent scenarios manager."""
        # Clear existing scenario tables
        for i in reversed(range(self.scenarios_layout.count())):
            child = self.scenarios_layout.takeAt(i).widget()
            if child:
                child.deleteLater()
        
        # Get scenarios from parent
        if not self.parent:
            self.show_no_data_message("No parent window available.")
            return
        
        # Get scenarios from the scenarios manager page
        try:
            if hasattr(self.parent, 'scenarios_manager_page'):
                scenarios_manager = self.parent.scenarios_manager_page
                scenarios = scenarios_manager.scenarios
            else:
                self.show_no_data_message("Cannot access scenarios manager.")
                return
        except Exception as e:
            self.show_no_data_message(f"Error accessing scenarios: {str(e)}")
            return
        if not scenarios:
            self.show_no_data_message("No scenarios available for comparison.\n\nGo back to create some scenarios first.")
            return
        # Create a ScenarioComparisonTable widget for each scenario
        for index, scenario in enumerate(scenarios, 1):
            scenario_widget = ScenarioComparisonTable(scenario, index)
            # Add each widget with stretch factor 1 to distribute space evenly
            self.scenarios_layout.addWidget(scenario_widget, 1)
        # Update the scorebar with scenario data
        self.update_scorebar(scenarios)

    def show_no_data_message(self, message):
        """Show a message when no data is available."""
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(get_medium_font())
        message_label.setWordWrap(True)
        self.scenarios_layout.addWidget(message_label)

    def update_scorebar(self, scenarios):
        """Update the scorebar with scenario data."""
        if not scenarios:
            return
        
        # Calculate total EIQ for each scenario
        scenarios_data = []
        for index, scenario in enumerate(scenarios, 1):
            total_eiq = 0
            if scenario.applications:
                for app in scenario.applications:
                    if app.field_eiq is not None:
                        total_eiq += app.field_eiq
            
            scenarios_data.append({
                'name': scenario.name or "Unnamed Scenario",
                'value': total_eiq,
                'index': index
            })
        
        # Set scenarios data to the scorebar
        if scenarios_data:
            self.score_bar.set_scenarios(scenarios_data)
    
    def go_back(self):
        """Navigate back to the season planner page."""
        if self.parent:
            # Navigate back to season planner page (index 2)
            self.parent.navigate_to_page(2)