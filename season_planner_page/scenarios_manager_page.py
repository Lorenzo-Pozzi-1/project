"""
Scenarios Manager page for the LORENZO POZZI Pesticide App.

This module provides the main interface for managing multiple pesticide
application scenarios through tabs.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QMessageBox, QInputDialog, QSpacerItem)
from common.styles import (MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, 
    SECONDARY_BUTTON_STYLE, get_title_font)
from common.widgets import HeaderWithBackButton, ContentFrame, ScoreBar
from season_planner_page.scenario_tab import ScenarioTabPage
from data.scenario_model import Scenario

class ScenariosManagerPage(QWidget):
    """
    Container for multiple scenario tabs with management functionality.
    
    This page serves as the main interface for the Season Planner feature,
    allowing users to create, edit, and compare multiple scenarios.
    """
    
    def __init__(self, parent=None):
        """Initialize the scenarios manager page."""
        super().__init__(parent)
        self.parent = parent
        self.scenarios = []  # List of all scenarios
        self.scenario_tabs = {}  # Map scenario names to tab pages
        self.setup_ui()
        self.add_new_scenario()  # Start with one default scenario
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button
        header = HeaderWithBackButton("Season Planner - Scenarios")
        header.back_clicked.connect(self.parent.go_home)
        
        # Add buttons for scenario operations
        buttons_layout = QHBoxLayout()
        
        self.add_scenario_btn = QPushButton("New Scenario")
        self.add_scenario_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.add_scenario_btn.clicked.connect(self.add_new_scenario)
        
        self.clone_scenario_btn = QPushButton("Clone Current")
        self.clone_scenario_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.clone_scenario_btn.clicked.connect(self.clone_current_scenario)
        
        self.rename_scenario_btn = QPushButton("Rename")
        self.rename_scenario_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.rename_scenario_btn.clicked.connect(self.rename_current_scenario)
        
        self.delete_scenario_btn = QPushButton("Delete")
        self.delete_scenario_btn.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.delete_scenario_btn.clicked.connect(self.delete_current_scenario)
        
        self.compare_btn = QPushButton("Compare Scenarios")
        self.compare_btn.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.compare_btn.clicked.connect(self.compare_scenarios)
        
        buttons_layout.addWidget(self.add_scenario_btn)
        buttons_layout.addWidget(self.clone_scenario_btn)
        buttons_layout.addWidget(self.rename_scenario_btn)
        buttons_layout.addWidget(self.delete_scenario_btn)
        buttons_layout.addSpacerItem(QSpacerItem(20, 10))
        buttons_layout.addWidget(self.compare_btn)
        buttons_layout.addStretch(1)
        
        # Set fixed width for buttons
        for btn in [self.add_scenario_btn, self.clone_scenario_btn, 
                   self.rename_scenario_btn, self.delete_scenario_btn, 
                   self.compare_btn]:
            btn.setFixedWidth(150)
        
        header_widget = QWidget()
        header_widget.setLayout(buttons_layout)
        header.layout().addWidget(header_widget)
        
        main_layout.addWidget(header)
        
        # Tab widget for scenarios
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.on_tab_close_requested)
        self.tab_widget.currentChanged.connect(self.on_current_tab_changed)
        
        main_layout.addWidget(self.tab_widget)
        
        # EIQ Results Display with Score Bar
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Title
        results_title = QLabel("Scenario EIQ Impact")
        results_title.setFont(get_title_font(size=16))
        results_layout.addWidget(results_title)
        
        # Create score bar with custom thresholds and labels
        self.eiq_score_bar = ScoreBar(
            thresholds=[200, 500, 800],
            labels=["Leading", "Advanced", "Engaged", "Onboarding"],
            min_value=0,
            max_value=800,
            title_text="RegenAg framework class:"
        )
        self.eiq_score_bar.set_value(0, "No applications")
        results_layout.addWidget(self.eiq_score_bar)
        
        # Add information labels (EIQ and application count)
        eiq_info_layout = QHBoxLayout()
        eiq_info_layout.addWidget(QLabel("Total Field EIQ:"))
        self.total_eiq_value = QLabel("0")
        eiq_info_layout.addWidget(self.total_eiq_value)
        
        eiq_info_layout.addSpacing(20)
        
        eiq_info_layout.addWidget(QLabel("Applications Count:"))
        self.applications_count_value = QLabel("0")
        eiq_info_layout.addWidget(self.applications_count_value)
        
        eiq_info_layout.addStretch(1)
        results_layout.addLayout(eiq_info_layout)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
        
        # Update button states
        self.update_buttons_state()
    
    def add_new_scenario(self, scenario=None):
        """
        Add a new scenario tab.
        
        Args:
            scenario: Existing Scenario object or None for a new one
        """
        if not isinstance(scenario, Scenario):
            # Ensure we create a proper Scenario object
            scenario = Scenario(f"Scenario {len(self.scenarios) + 1}")
        
        # Create tab page
        scenario_page = ScenarioTabPage(self, scenario)
        scenario_page.scenario_changed.connect(self.on_scenario_changed)
        
        # Add to tab widget - ensure scenario.name exists and is a string
        tab_name = getattr(scenario, 'name', f"Scenario {len(self.scenarios) + 1}")
        tab_index = self.tab_widget.addTab(scenario_page, tab_name)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Store references
        self.scenarios.append(scenario)
        self.scenario_tabs[tab_name] = scenario_page
        
        # Update UI state
        self.update_buttons_state()
        self.update_eiq_display()
    
    def clone_current_scenario(self):
        """Clone the current scenario and add it as a new tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        current_page = self.tab_widget.widget(current_index)
        current_scenario = current_page.get_scenario()
        
        # Clone the scenario
        new_scenario = current_scenario.clone()
        
        # Add as new tab
        self.add_new_scenario(new_scenario)
    
    def rename_current_scenario(self):
        """Rename the current scenario tab."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        current_page = self.tab_widget.widget(current_index)
        current_scenario = current_page.get_scenario()
        
        # Show dialog to get new name
        new_name, ok = QInputDialog.getText(
            self, "Rename Scenario", "Enter new scenario name:", 
            text=current_scenario.name
        )
        
        if ok and new_name:
            # Update scenario name
            old_name = current_scenario.name
            current_scenario.name = new_name
            
            # Update tab name
            self.tab_widget.setTabText(current_index, new_name)
            
            # Update dictionary entry
            self.scenario_tabs[new_name] = self.scenario_tabs.pop(old_name)
            
            # Emit change signal
            self.on_scenario_changed(current_scenario)
    
    def delete_current_scenario(self):
        """Delete the current scenario tab with confirmation."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            return
        
        self.on_tab_close_requested(current_index)
    
    def on_tab_close_requested(self, index):
        """
        Handle tab close request with confirmation.
        
        Args:
            index: Index of the tab to close
        """
        # Prevent closing the last tab
        if self.tab_widget.count() <= 1:
            QMessageBox.information(
                self, "Cannot Delete", 
                "Cannot delete the last scenario. At least one scenario must remain."
            )
            return
        
        scenario_page = self.tab_widget.widget(index)
        scenario = scenario_page.get_scenario()
        
        # Confirm deletion with dialog
        result = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove scenario '{scenario.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self.tab_widget.removeTab(index)
            self.scenarios.remove(scenario)
            del self.scenario_tabs[scenario.name]  # Using name instead of ID
            self.update_buttons_state()
            self.update_eiq_display()
    
    def on_current_tab_changed(self, index):
        """
        Handle tab selection change.
        
        Args:
            index: Index of the newly selected tab
        """
        self.update_buttons_state()
        self.update_eiq_display()
    
    def on_scenario_changed(self, scenario):
        """
        Handle changes to a scenario.
        
        Args:
            scenario: The changed Scenario object
        """
        # Find the scenario page - we need this since name may have changed
        scenario_page = None
        for page in [self.tab_widget.widget(i) for i in range(self.tab_widget.count())]:
            if page.get_scenario() is scenario:
                scenario_page = page
                break
        
        if scenario_page:
            # Find the tab index
            for i in range(self.tab_widget.count()):
                if self.tab_widget.widget(i) is scenario_page:
                    # Update tab text
                    self.tab_widget.setTabText(i, scenario.name)
                    break
                    
            # Update the scenario tabs dictionary if name changed
            for old_name in list(self.scenario_tabs.keys()):
                if self.scenario_tabs[old_name] is scenario_page and old_name != scenario.name:
                    # The name changed, so update the dictionary
                    self.scenario_tabs[scenario.name] = scenario_page
                    del self.scenario_tabs[old_name]
                    break
        
        self.update_eiq_display()
    
    def update_buttons_state(self):
        """Update the enabled state of buttons based on current state."""
        has_tabs = self.tab_widget.count() > 0
        
        # Enable/disable buttons that require a current tab
        self.clone_scenario_btn.setEnabled(has_tabs)
        self.rename_scenario_btn.setEnabled(has_tabs)
        self.delete_scenario_btn.setEnabled(has_tabs and self.tab_widget.count() > 1)
        self.compare_btn.setEnabled(self.tab_widget.count() > 1)
    
    def update_eiq_display(self):
        """Update the EIQ display based on current scenario."""
        current_index = self.tab_widget.currentIndex()
        if current_index < 0:
            # No tabs, reset display
            self.eiq_score_bar.set_value(0, "No scenario selected")
            self.total_eiq_value.setText("0")
            self.applications_count_value.setText("0")
            return
        
        # Get current scenario page and data
        current_page = self.tab_widget.widget(current_index)
        total_eiq = current_page.get_total_field_eiq()
        applications = current_page.applications_container.get_applications()
        
        # Update score bar
        self.eiq_score_bar.set_value(
            total_eiq if total_eiq > 0 else 0, 
            "" if total_eiq > 0 else "No applications"
        )
        
        # Update labels
        self.total_eiq_value.setText(f"{total_eiq:.2f}")
        self.applications_count_value.setText(str(len(applications)))
    
    def compare_scenarios(self):
        """Compare selected scenarios (placeholder for future implementation)."""
        QMessageBox.information(
            self, "Not Implemented", 
            "The comparison feature will be implemented in a future update."
        )
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        for name, tab_page in self.scenario_tabs.items():
            tab_page.refresh_product_data()