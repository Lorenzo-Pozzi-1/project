"""
Season Planner page for the Lorenzo Pozzi Pesticide App

This module defines the SeasonPlannerPage class which serves as the main
container for the season planner functionality.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget
from PySide6.QtCore import Qt

from ui.common.styles import (
    MARGIN_LARGE, SPACING_MEDIUM, SECONDARY_BUTTON_STYLE
)
from ui.common.widgets import HeaderWithBackButton

from ui.season_planner.scenario_editor import ScenarioEditor
from ui.season_planner.scenario_comparison import ScenarioComparison


class SeasonPlannerPage(QWidget):
    """
    Season Planner page that allows planning and comparing pesticide applications.
    
    This class serves as the main container for the season planner functionality,
    managing navigation between scenario editing and comparison views.
    """
    def __init__(self, parent=None):
        """Initialize the season planner page."""
        super().__init__(parent)
        self.parent = parent
        self.scenarios = {}  # Dictionary to store scenario data
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        self.main_layout.setSpacing(SPACING_MEDIUM)
        
        # Initialize both views
        self.init_planner_view()
        self.init_comparison_view()
        
        # Show the planner view initially
        self.show_planner_view()
    
    def init_planner_view(self):
        """Initialize the planner view layout."""
        # Planner container widget
        self.planner_widget = QWidget()
        planner_layout = QVBoxLayout(self.planner_widget)
        planner_layout.setContentsMargins(0, 0, 0, 0)
        
        # Header with back button
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        planner_layout.addWidget(header)
        
        # Button row under the header
        button_row = QHBoxLayout()
        
        # Add spacer to push compare button to right
        button_row.addStretch()
        
        # Compare scenarios button
        compare_button = QPushButton("Compare scenarios >")
        compare_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        compare_button.clicked.connect(self.show_comparison_view)
        button_row.addWidget(compare_button)
        
        planner_layout.addLayout(button_row)
        
        # Create tab widget for scenarios
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(True)
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # Add first scenario
        self.add_scenario("Scenario 1")
        
        # Add a "+" tab that adds new scenarios
        self.tab_widget.addTab(QWidget(), "+")
        self.tab_widget.tabBarClicked.connect(self.handle_tab_click)
        
        planner_layout.addWidget(self.tab_widget)
    
    def init_comparison_view(self):
        """Initialize the comparison view layout."""
        # Create comparison widget
        self.comparison_widget = ScenarioComparison(self)
    
    def add_scenario(self, name=None):
        """Add a new scenario tab."""
        if name is None:
            # Find next available scenario number
            i = 1
            while f"Scenario {i}" in self.scenarios:
                i += 1
            name = f"Scenario {i}"
        
        # Create new scenario tab
        scenario_tab = ScenarioEditor(name, self)
        
        # Add the tab before the "+" tab
        insert_index = self.tab_widget.count() - 1
        self.tab_widget.insertTab(insert_index, scenario_tab, name)
        
        # Store scenario in dictionary
        self.scenarios[name] = scenario_tab
        
        # Switch to the new tab
        self.tab_widget.setCurrentIndex(insert_index)
    
    def handle_tab_click(self, index):
        """Handle tab click event."""
        # Check if the clicked tab is the "+" tab
        if index == self.tab_widget.count() - 1:
            self.add_scenario()
    
    def close_tab(self, index):
        """Close a tab when the close button is clicked."""
        # Don't allow closing the "+" tab
        if index == self.tab_widget.count() - 1:
            return
        
        # Don't allow closing if it's the only scenario tab
        if self.tab_widget.count() <= 2:  # 1 scenario tab + "+" tab
            return
        
        # Get the tab name
        tab_name = self.tab_widget.tabText(index)
        
        # Remove the tab
        self.tab_widget.removeTab(index)
        
        # Remove from scenarios dictionary
        if tab_name in self.scenarios:
            del self.scenarios[tab_name]
    
    def show_planner_view(self):
        """Switch to planner view."""
        # First clear the layout
        self.clear_layout()
        
        # Add planner widget
        self.main_layout.addWidget(self.planner_widget)
        self.planner_widget.show()
    
    def show_comparison_view(self):
        """Switch to comparison view."""
        # Update comparison data from current scenarios
        comparison_data = {}
        for name, scenario_tab in self.scenarios.items():
            comparison_data[name] = scenario_tab.get_data_for_comparison()
        
        self.comparison_widget.update_comparison(comparison_data)
        
        # First clear the layout
        self.clear_layout()
        
        # Add comparison widget
        self.main_layout.addWidget(self.comparison_widget)
        self.comparison_widget.show()
    
    def clear_layout(self):
        """Clear the main layout."""
        # Hide all widgets
        if hasattr(self, 'planner_widget'):
            self.planner_widget.hide()
        if hasattr(self, 'comparison_widget'):
            self.comparison_widget.hide()
        
        # Remove all widgets from layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().hide()