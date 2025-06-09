"""
Scenarios Comparison Page for the Season Planner.

A container page that displays multiple ScenarioComparisonTable widgets
to compare scenarios side by side.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QScrollArea)
from PySide6.QtCore import Qt

from common import (HeaderWithHomeButton, get_margin_large, get_spacing_medium,
                   get_medium_font)
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
        for scenario in scenarios:
            scenario_widget = ScenarioComparisonTable(scenario)
            self.scenarios_layout.addWidget(scenario_widget)
        
        # Add stretch to left-align scenarios
        self.scenarios_layout.addStretch()
    
    def show_no_data_message(self, message):
        """Show a message when no data is available."""
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setFont(get_medium_font())
        message_label.setWordWrap(True)
        self.scenarios_layout.addWidget(message_label)
    
    def go_back(self):
        """Navigate back to the scenarios manager page."""
        if self.parent:
            # Navigate back to scenarios manager page (index 2)
            self.parent.navigate_to_page(2)