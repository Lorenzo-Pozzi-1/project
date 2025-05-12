"""
New Season page for the LORENZO POZZI Pesticide App's Season Planner.

This module defines the NewSeasonPage class which allows users to create
a new season plan from scratch with multiple scenarios.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTabWidget, QFrame
from PySide6.QtCore import Qt
from common.styles import MARGIN_LARGE, SECONDARY_BUTTON_STYLE, SPACING_LARGE, PRIMARY_BUTTON_STYLE
from common.widgets import HeaderWithBackButton
from season_planner.models import Scenario
from season_planner.scenario_widget import ScenarioWidget

class NewSeasonPage(QWidget):
    """
    New Season page for creating a season plan from scratch.
    
    This page allows users to create multiple scenarios and compare them.
    """
    
    def __init__(self, parent=None):
        """Initialize the new season page."""
        super().__init__(parent)
        self.parent = parent
        self.scenarios = []  # List of Scenario objects
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Header with back button and title
        self.header = HeaderWithBackButton("New Season Planning")
        self.header.back_clicked.connect(self.go_back)
        main_layout.addWidget(self.header)
        
        # Compare Scenarios button - add to right side of header
        self.compare_button = QPushButton("Compare Scenarios")
        self.compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.compare_button.clicked.connect(self.compare_scenarios)
        self.header.layout().addWidget(self.compare_button)

        # Reset button next to Compare button
        self.reset_button = QPushButton("Reset")
        self.reset_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.reset_button.clicked.connect(self.reset_current_scenario)
        self.header.layout().addWidget(self.reset_button)
        
        # Tab widget for scenarios
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_scenario_tab)

        # EIQ gradient bar below tab_widget
        gradient_label = QLabel("Low / Med / High Environmental Impact")
        gradient_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(gradient_label)

        # Create a gradient bar
        self.gradient_bar = QFrame()
        self.gradient_bar.setMinimumHeight(20)
        self.gradient_bar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 #77DD77,
                                        stop:0.5 #FFF275,
                                        stop:1 #FF6961);
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.gradient_bar)
        
        # Add initial scenario tab
        self.add_scenario_tab()
        
        # Add "+" tab for adding new scenarios
        self.tab_widget.addTab(QWidget(), "+")
        self.tab_widget.tabBarClicked.connect(self.handle_tab_click)
        
        main_layout.addWidget(self.tab_widget)
    
    def add_scenario_tab(self):
        """Add a new scenario tab with the scenario widget."""
        # Create new scenario data model
        scenario = Scenario(name=f"Scenario {len(self.scenarios) + 1}")
        self.scenarios.append(scenario)
        
        # Create the scenario widget
        scenario_widget = ScenarioWidget(scenario=scenario)
        scenario_widget.scenario_changed.connect(self.on_scenario_changed)
        
        # Add the tab
        scenario_count = self.tab_widget.count()
        # Don't count the "+" tab if it exists
        if scenario_count > 0 and self.tab_widget.tabText(scenario_count - 1) == "+":
            scenario_count -= 1
            
        self.tab_widget.insertTab(scenario_count, scenario_widget, f"Scenario {scenario_count + 1}")
        self.tab_widget.setCurrentIndex(scenario_count)
    
    def handle_tab_click(self, index):
        """Handle tab clicks, particularly for the "+" tab."""
        if index == self.tab_widget.count() - 1 and self.tab_widget.tabText(index) == "+":
            self.add_scenario_tab()
    
    def close_scenario_tab(self, index):
        """Close a scenario tab if it's not the last one or the "+" tab."""
        # Don't close if it's the "+" tab
        if self.tab_widget.tabText(index) == "+":
            return
            
        # Don't close if it's the only scenario tab
        scenario_tabs = 0
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) != "+":
                scenario_tabs += 1
                
        if scenario_tabs <= 1:
            return
            
        # Remove the scenario from our data list
        if 0 <= index < len(self.scenarios):
            del self.scenarios[index]
            
        # Close the tab
        self.tab_widget.removeTab(index)
        
        # Rename remaining tabs to keep them sequential
        for i in range(self.tab_widget.count() - 1):  # Skip the "+" tab
            self.tab_widget.setTabText(i, f"Scenario {i + 1}")
            
            # Also update scenario names
            if i < len(self.scenarios):
                self.scenarios[i].name = f"Scenario {i + 1}"
    
    def compare_scenarios(self):
        """Compare the created scenarios."""
        print("Scenarios will be compared")
        # This will be implemented later
    
    def go_back(self):
        """Go back to the main season planner page."""
        if self.parent:
            self.parent.go_back_to_main()
    
    def on_scenario_changed(self):
        """Handle changes to a scenario."""
        # This will be used for autosaving, etc.
        pass

    def reset_current_scenario(self):
        """Reset the current scenario to empty state."""
        current_index = self.tab_widget.currentIndex()
        
        # Check if it's a valid scenario tab
        if current_index >= 0 and current_index < len(self.scenarios):
            # Get the scenario widget
            widget = self.tab_widget.widget(current_index)
            if isinstance(widget, ScenarioWidget):
                widget.clear_scenario()