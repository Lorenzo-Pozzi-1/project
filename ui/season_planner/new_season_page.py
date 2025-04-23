"""
New Season page for the LORENZO POZZI Pesticide App's Season Planner.

This module defines the NewSeasonPage class which allows users to create
a new season plan from scratch with multiple scenarios.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QTabWidget, QTableWidget, QFrame, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, Signal

from ui.common.styles import (
    MARGIN_LARGE, SPACING_LARGE, get_subtitle_font, get_body_font,
    PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
)
from ui.common.widgets import HeaderWithBackButton, ContentFrame, ToxicityBar

class NewSeasonPage(QWidget):
    """
    New Season page for creating a season plan from scratch.
    
    This page allows users to create multiple scenarios and compare them.
    """
    
    def __init__(self, parent=None):
        """Initialize the new season page."""
        super().__init__(parent)
        self.parent = parent
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
        
        # Tab widget for scenarios
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_scenario_tab)
        
        # Add initial scenario tab
        self.add_scenario_tab()
        
        # Add "+" tab for adding new scenarios
        self.tab_widget.addTab(QWidget(), "+")
        self.tab_widget.tabBarClicked.connect(self.handle_tab_click)
        
        main_layout.addWidget(self.tab_widget)
        
        # Replace the custom gradient bar with ToxicityBar
        self.toxicity_bar = ToxicityBar(self)
        self.toxicity_bar.title_text = "Environmental Impact"
        self.toxicity_bar.set_value(0, "No data")  # Initialize with no value
        
        main_layout.addWidget(self.toxicity_bar)
    
    def add_scenario_tab(self):
        """Add a new scenario tab with a placeholder table."""
        # Create tab content widget
        tab_content = QWidget()
        tab_layout = QVBoxLayout(tab_content)
        
        # Add placeholder table
        table = QTableWidget(10, 5)  # 10 rows, 5 columns for placeholder
        table.setHorizontalHeaderLabels(["Date", "Product", "Rate", "Application Method", "Notes"])
        table.horizontalHeader().setStretchLastSection(True)
        tab_layout.addWidget(table)
        
        # Add the tab
        scenario_count = self.tab_widget.count()
        # Don't count the "+" tab if it exists
        if scenario_count > 0 and self.tab_widget.tabText(scenario_count - 1) == "+":
            scenario_count -= 1
            
        self.tab_widget.insertTab(scenario_count, tab_content, f"Scenario {scenario_count + 1}")
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
            
        # Close the tab
        self.tab_widget.removeTab(index)
        
        # Rename remaining tabs to keep them sequential
        for i in range(self.tab_widget.count() - 1):  # Skip the "+" tab
            self.tab_widget.setTabText(i, f"Scenario {i + 1}")
    
    def compare_scenarios(self):
        """Compare the created scenarios."""
        print("Scenarios will be compared")
        # Placeholder for future functionality
    
    def go_back(self):
        """Go back to the main season planner page."""
        if self.parent:
            self.parent.go_back_to_main()