"""
STIR Calculator page

This module defines the STIRCalculatorPage class which provides a
tabbed interface for managing STIR scenarios similar to the EIQ season planner.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QTableWidget, QTableWidgetItem, QHeaderView, QTabBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QBrush, QColor
from common.constants import get_margin_large, get_spacing_large, get_spacing_medium
from common.styles import (
    get_title_font, get_large_font, get_subtitle_font, get_medium_font,
    INFO_TEXT_STYLE, GENERIC_TABLE_STYLE
)
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button, HeaderWithHomeButton
from common.widgets.scorebar import ScoreBar

class STIRScenarioTab(QWidget):
    """Individual STIR scenario tab with table and scorebar."""
    
    def __init__(self, scenario_name="Scenario", parent=None):
        """Initialize the STIR scenario tab."""
        super().__init__(parent)
        self.scenario_name = scenario_name
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the scenario tab."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), 
                                     get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # STIR Operations Table
        table_frame = ContentFrame()
        table_layout = QVBoxLayout()
        
        # Table title
        table_title = QLabel("STIR Operations")
        table_title.setFont(get_subtitle_font())
        table_layout.addWidget(table_title)
        
        # Create operations table
        self.operations_table = QTableWidget()
        self.operations_table.setStyleSheet(GENERIC_TABLE_STYLE)
        self.operations_table.setAlternatingRowColors(True)
        self.setup_operations_table()
        table_layout.addWidget(self.operations_table)
        
        table_frame.layout.addLayout(table_layout)
        main_layout.addWidget(table_frame)
        
        # Results section with scorebar
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Total STIR display
        total_layout = QHBoxLayout()
        total_label = QLabel("TOTAL STIR:")
        total_label.setFont(get_subtitle_font(bold=True))
        total_layout.addWidget(total_label)
        
        self.total_stir_value = QLabel("268")
        self.total_stir_value.setFont(get_subtitle_font(bold=True, size=18))
        total_layout.addWidget(self.total_stir_value)
        
        total_layout.addStretch()
        results_layout.addLayout(total_layout)
        
        # Custom STIR scorebar (Light to Intense)
        self.stir_scorebar = ScoreBar(preset="calculator")  # We'll customize this
        # Override the scorebar settings for STIR
        self.stir_scorebar.config.title = "Tillage Intensity:"
        self.stir_scorebar.config.thresholds = [100, 200, 400]
        self.stir_scorebar.config.labels = ["Light", "Medium", "Intense", "Very Intense"]
        self.stir_scorebar.config.min_value = 0
        self.stir_scorebar.config.max_value = 500
        self.stir_scorebar.set_value(268, "Intense")
        
        results_layout.addWidget(self.stir_scorebar)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def setup_operations_table(self):
        """Set up the operations table with placeholder data."""
        # Set up table structure
        self.operations_table.setRowCount(7)  # 3 pre-plant + 2 in-season + 1 harvest + 1 empty
        self.operations_table.setColumnCount(6)
        
        # Set headers
        headers = ["Machine", "Depth (cm)", "Speed (km/h)", "N of passes", "STIR", "Total"]
        self.operations_table.setHorizontalHeaderLabels(headers)
        
        # Configure column widths
        header = self.operations_table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # Add placeholder data
        operations_data = [
            # Operation category, Machine, Depth, Speed, Passes, STIR, Total, row_color
            ("Pre-plant", "Disk harrow", "15", "10", "2", "52", "135", "#FFE5E5"),  # Light red
            ("", "Chisel plough", "30", "12", "1", "38", "", ""),
            ("", '"MyMachine"', "15", "12", "1", "45", "", ""),
            ("In-season", "Potato planter", "20", "9.0", "1", "29", "49", "#E5FFE5"),  # Light green
            ("", "Hiller", "35", "12", "1", "20", "", ""),
            ("Harvest", "Potato harvester", "30", "6.0", "1", "84", "84", "#FFE5E5"),  # Light red
            ("", "", "", "", "", "", "", "")  # Empty row
        ]
        
        current_category = ""
        for row, (category, machine, depth, speed, passes, stir, total, row_color) in enumerate(operations_data):
            # Machine name
            machine_item = QTableWidgetItem(machine)
            if category and category != current_category:
                # This is a category header row
                machine_item.setText(f"{category} operations")
                machine_item.setFont(get_medium_font(bold=True))
                if row_color:
                    machine_item.setBackground(QBrush(QColor(row_color)))
                current_category = category
            else:
                machine_item.setText(machine)
                if row_color:
                    machine_item.setBackground(QBrush(QColor(row_color)))
            
            self.operations_table.setItem(row, 0, machine_item)
            
            # Other columns
            columns_data = [depth, speed, passes, stir, total]
            for col, value in enumerate(columns_data, 1):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                if row_color:
                    item.setBackground(QBrush(QColor(row_color)))
                
                # Color code STIR values
                if col == 4 and value:  # STIR column
                    try:
                        stir_val = int(value)
                        if stir_val < 30:
                            item.setBackground(QBrush(QColor("#90EE90")))  # Light green
                        elif stir_val < 50:
                            item.setBackground(QBrush(QColor("#FFFF99")))  # Light yellow
                        else:
                            item.setBackground(QBrush(QColor("#FFB6C1")))  # Light red
                    except ValueError:
                        pass
                
                self.operations_table.setItem(row, col, item)
        
        # Set row heights
        self.operations_table.verticalHeader().setVisible(False)
        for row in range(self.operations_table.rowCount()):
            self.operations_table.setRowHeight(row, 35)


class CustomSTIRTabBar(QTabBar):
    """Custom tab bar for STIR scenarios with double-click to rename."""
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click to rename tabs."""
        tab_index = self.tabAt(event.pos())
        if tab_index >= 0:
            # For now, just print - will implement rename later
            print(f"Double-clicked tab {tab_index} - rename functionality coming soon!")
        super().mouseDoubleClickEvent(event)


class STIRCalculatorPage(QWidget):
    """
    STIR Calculator page with tabbed scenario management.
    
    Similar to the EIQ season planner, this page manages multiple
    STIR calculation scenarios in tabs.
    """
    
    def __init__(self, parent=None):
        """Initialize the STIR calculator page."""
        super().__init__(parent)
        self.parent = parent
        self.scenario_tabs = {}  # Dictionary to track scenario tabs
        self.setup_ui()
        self.add_initial_scenarios()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), 
                                     get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with back button and action buttons
        header = HeaderWithHomeButton("STIR Calculator")
        header.back_clicked.connect(self.go_back_to_stir_home)
        
        # Wrap action buttons in ContentFrame
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        # Create action buttons
        buttons = {
            "New Scenario": ("yellow", self.new_scenario),
            "Duplicate Current": ("white", self.duplicate_current_scenario),
            "Compare Scenarios": ("yellow", self.compare_scenarios),
            "Export": ("special", self.export_scenarios)
        }
        
        self.action_buttons = {}
        
        for text, (style, callback) in buttons.items():
            btn = create_button(text, style=style, callback=callback, parent=self)
            buttons_layout.addWidget(btn)
            self.action_buttons[text] = btn
        
        buttons_frame.layout.addLayout(buttons_layout)
        header.layout().addWidget(buttons_frame)
        
        main_layout.addWidget(header)
        
        # Tabs section wrapped in ContentFrame
        tabs_frame = ContentFrame()
        tabs_layout = QVBoxLayout()
        
        # Tab widget for STIR scenarios
        self.tab_widget = QTabWidget()
        self.custom_tab_bar = CustomSTIRTabBar()
        self.tab_widget.setTabBar(self.custom_tab_bar)
        self.tab_widget.setMovable(True)  # Enable drag-to-reorder
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        tabs_layout.addWidget(self.tab_widget)
        tabs_frame.layout.addLayout(tabs_layout)
        main_layout.addWidget(tabs_frame)
    
    def add_initial_scenarios(self):
        """Add initial placeholder scenarios."""
        # Add two example scenarios
        scenario1 = STIRScenarioTab("Scenario 1", self)
        self.tab_widget.addTab(scenario1, "Scenario 1")
        self.scenario_tabs["Scenario 1"] = scenario1
        
        scenario2 = STIRScenarioTab("Scenario 2", self)
        self.tab_widget.addTab(scenario2, "Scenario 2")
        self.scenario_tabs["Scenario 2"] = scenario2
        
        # Set the first tab as current
        self.tab_widget.setCurrentIndex(0)
        self.update_ui_state()
    
    def new_scenario(self):
        """Create a new STIR scenario."""
        # Generate unique name
        base_name = "New Scenario"
        counter = 1
        while f"{base_name} {counter}" in self.scenario_tabs:
            counter += 1
        
        scenario_name = f"{base_name} {counter}"
        
        # Create new tab
        new_scenario = STIRScenarioTab(scenario_name, self)
        tab_index = self.tab_widget.addTab(new_scenario, scenario_name)
        self.scenario_tabs[scenario_name] = new_scenario
        
        # Switch to the new tab
        self.tab_widget.setCurrentIndex(tab_index)
        self.update_ui_state()
        print(f"Created new STIR scenario: {scenario_name}")
    
    def duplicate_current_scenario(self):
        """Duplicate the current STIR scenario."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        current_name = self.tab_widget.tabText(current_index)
        
        # Generate unique name for duplicate
        base_name = f"{current_name} Copy"
        counter = 1
        while f"{base_name} {counter}" in self.scenario_tabs:
            counter += 1
        
        duplicate_name = f"{base_name} {counter}"
        
        # Create duplicate tab
        duplicate_scenario = STIRScenarioTab(duplicate_name, self)
        tab_index = self.tab_widget.addTab(duplicate_scenario, duplicate_name)
        self.scenario_tabs[duplicate_name] = duplicate_scenario
        
        # Switch to the duplicate tab
        self.tab_widget.setCurrentIndex(tab_index)
        self.update_ui_state()
        print(f"Duplicated STIR scenario: {duplicate_name}")
    
    def compare_scenarios(self):
        """Compare STIR scenarios."""
        print("Compare STIR scenarios - coming soon!")
        # This would navigate to a comparison page similar to EIQ
    
    def export_scenarios(self):
        """Export STIR scenarios."""
        print("Export STIR scenarios - coming soon!")
        # This would export scenarios to Excel
    
    def on_tab_changed(self, index):
        """Handle tab change events."""
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update UI state based on current tabs."""
        has_tabs = self.tab_widget.count() > 0
        
        # Enable/disable buttons based on tab availability
        self.action_buttons["Duplicate Current"].setEnabled(has_tabs)
        self.action_buttons["Compare Scenarios"].setEnabled(has_tabs and self.tab_widget.count() > 1)
        self.action_buttons["Export"].setEnabled(has_tabs)
    
    def go_back_to_stir_home(self):
        """Navigate back to the STIR home page."""
        self.parent.navigate_to_page(6)  # STIR home page is at index 6