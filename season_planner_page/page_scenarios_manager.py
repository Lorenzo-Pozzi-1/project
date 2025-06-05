"""
Scenarios Manager Page for the Season Planner.

Main interface for managing multiple pesticide application scenarios
using the new table-based interface.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QMessageBox, QInputDialog, QDialog
from PySide6.QtCore import QCoreApplication

from common import (
    ContentFrame, HeaderWithHomeButton, calculation_tracer, create_button, 
    ScoreBar, get_margin_large, get_spacing_medium, get_subtitle_font
)
from season_planner_page.tab_scenario import ScenarioTabPage
from season_planner_page.import_scenario import ImportScenarioDialog
from data import Scenario


class ScenariosManagerPage(QWidget):
    """
    Container for multiple scenario tabs with management functionality.
    
    This page serves as the main interface for the Season Planner feature,
    using the new table-based applications interface for better performance
    and user experience.
    """
    
    def __init__(self, parent=None):
        """Initialize the scenarios manager page."""
        super().__init__(parent)
        self.parent = parent
        self.scenarios = []  # List of all scenarios
        self.scenario_tabs = {}  # Map scenario names to tab pages
        self.setup_ui()
        self.add_new_scenario()  # Start with one default scenario
        calculation_tracer.clear()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with back button and operation buttons
        header = HeaderWithHomeButton("Season Planner - Scenarios")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Wrap buttons in ContentFrame
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        # Create buttons with fixed width
        buttons = {
            "Import Scenario": ("white", self.import_scenario),
            "New Scenario": ("yellow", self.add_new_scenario),
            "Clone Current": ("white", self.clone_current_scenario),
            "Rename": ("white", self.rename_current_scenario),
            "Delete": ("white", self.delete_current_scenario),
            "Compare Scenarios": ("yellow", self.compare_scenarios),
            "Export": ("special", self.export)
        }
        
        self.action_buttons = {}
        
        for text, (style, callback) in buttons.items():
            btn = create_button(text, style=style, callback=callback, parent=self)
            buttons_layout.addWidget(btn)
            self.action_buttons[text] = btn
        
        buttons_frame.layout.addLayout(buttons_layout)
        header.layout().addWidget(buttons_frame)
        
        main_layout.addWidget(header)
        
        # Wrap tab widget in ContentFrame
        tabs_frame = ContentFrame()
        tabs_layout = QVBoxLayout()
        
        # Tab widget for scenarios
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.update_ui_state)
        
        tabs_layout.addWidget(self.tab_widget)
        tabs_frame.layout.addLayout(tabs_layout)
        main_layout.addWidget(tabs_frame)
        
        # EIQ Results Display
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()

        # Combined title with scenario info
        self.scenario_info_title = QLabel("New Scenario: 0 applications, field EIQ score: 0.00", font=get_subtitle_font())
        results_layout.addWidget(self.scenario_info_title)

        # Create score bar with custom thresholds and labels
        self.eiq_score_bar = ScoreBar(
            thresholds=[200, 500, 800, 2500],
            labels=["Leading", "Advanced", "Engaged", "Onboarding", "Out of range"],
            min_value=0,
            max_value=2500,
            title_text="RegenAg framework class:"
        )
        self.eiq_score_bar.set_value(0, "No applications")
        results_layout.addWidget(self.eiq_score_bar)

        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def generate_unique_name(self, base_name):
        """Generate a unique scenario name based on the given base name."""
        if base_name not in self.scenario_tabs:
            return base_name
            
        counter = 1
        while f"{base_name} ({counter})" in self.scenario_tabs:
            counter += 1
            
        return f"{base_name} ({counter})"
    
    def add_new_scenario(self, scenario=None):
        """Add a new scenario tab."""
        if not isinstance(scenario, Scenario):
            # Create a new scenario with a unique name
            base_name = f"Scenario {len(self.scenarios) + 1}"
            unique_name = self.generate_unique_name(base_name)
            scenario = Scenario(unique_name)
        else:
            # Ensure cloned scenario has a unique name
            scenario.name = self.generate_unique_name(scenario.name)
        
        # Create tab page
        tab_page = ScenarioTabPage(self, scenario)
        tab_page.scenario_changed.connect(self.on_scenario_changed)
        
        # Add to tab widget
        tab_index = self.tab_widget.addTab(tab_page, scenario.name)
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Store references
        self.scenarios.append(scenario)
        self.scenario_tabs[scenario.name] = tab_page
        
        # Update UI state
        self.update_ui_state()
    
    def get_current_scenario_page(self):
        """Get the current scenario page and its index."""
        index = self.tab_widget.currentIndex()
        if index < 0:
            return None, -1
        return self.tab_widget.widget(index), index
    
    def clone_current_scenario(self):
        """Clone the current scenario and add it as a new tab."""
        page, _ = self.get_current_scenario_page()
        if page:
            original_scenario = page.get_scenario()
            new_scenario = original_scenario.clone()
            self.add_new_scenario(new_scenario)
    
    def rename_current_scenario(self):
        """Rename the current scenario tab."""
        page, index = self.get_current_scenario_page()
        if not page:
            return
            
        scenario = page.get_scenario()
        old_name = scenario.name
        
        while True:
            # Show dialog to get new name
            new_name, ok = QInputDialog.getText(
                self, "Rename Scenario", "Enter new scenario name:", 
                text=old_name
            )
            
            if not ok or new_name == old_name:
                return
                
            # Check if name already exists
            if new_name in self.scenario_tabs and new_name != old_name:
                QMessageBox.warning(
                    self, "Name Already Exists", 
                    "Scenario names must be unique.",
                    QMessageBox.Ok
                )
                continue
                
            # Valid name - update scenario
            scenario.name = new_name
            self.tab_widget.setTabText(index, new_name)
            self.scenario_tabs[new_name] = self.scenario_tabs.pop(old_name)
            self.update_ui_state()
            break
    
    def delete_current_scenario(self):
        """Delete the current scenario tab with confirmation."""
        _, index = self.get_current_scenario_page()
        if index < 0:
            return
            
        page = self.tab_widget.widget(index)
        scenario = page.get_scenario()
        
        # Confirm deletion
        result = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove this scenario? '{scenario.name}'",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Handle deletion
            if self.tab_widget.count() <= 1:
                # Last tab - remove it and create a new blank one
                self.tab_widget.removeTab(index)
                self.scenarios.remove(scenario)
                del self.scenario_tabs[scenario.name]
                
                # Create a new blank scenario
                self.add_new_scenario()
            else:
                # Normal deletion - just remove the tab
                self.tab_widget.removeTab(index)
                self.scenarios.remove(scenario)
                del self.scenario_tabs[scenario.name]
                
            self.update_ui_state()
    
    def on_scenario_changed(self, scenario):
        """Handle changes to a scenario."""
        # Find the scenario page
        for i in range(self.tab_widget.count()):
            page = self.tab_widget.widget(i)
            if page.get_scenario() is scenario:
                old_name = self.tab_widget.tabText(i)
                
                # Validate name uniqueness if it has changed
                if old_name != scenario.name:
                    # If the new name already exists, revert to old name
                    if scenario.name in self.scenario_tabs and self.scenario_tabs[scenario.name] is not page:
                        QMessageBox.warning(
                            self, "Name Already Exists", 
                            "Scenario names must be unique.",
                            QMessageBox.Ok
                        )
                        # Revert the name
                        scenario.name = old_name
                    else:
                        # Update tab text
                        self.tab_widget.setTabText(i, scenario.name)
                        
                        # Update dictionary if name changed
                        self.scenario_tabs[scenario.name] = page
                        del self.scenario_tabs[old_name]
                
                break
                
        self.update_ui_state()
    
    def update_ui_state(self):
        """Update buttons state and EIQ display based on current state."""
        # Update buttons state
        has_tabs = self.tab_widget.count() > 0
        
        self.action_buttons["Clone Current"].setEnabled(has_tabs)
        self.action_buttons["Rename"].setEnabled(has_tabs)
        self.action_buttons["Delete"].setEnabled(has_tabs)
        
        # Update EIQ display
        page, _ = self.get_current_scenario_page()
        if not page:
            scenario_name = "No scenario selected"
            total_eiq = 0.0
            applications_count = 0
        else:
            scenario_name = page.get_scenario().name
            total_eiq = page.get_total_field_eiq()
            applications = page.applications_table.get_applications()
            applications_count = len(applications)
        
        # Update combined title
        self.scenario_info_title.setText(
            f"{scenario_name}: {applications_count} applications, field EIQ score: {total_eiq:.2f}"
        )
        
        self.eiq_score_bar.set_value(
            total_eiq if total_eiq > 0 else 0, 
            "" if total_eiq > 0 else "No applications"
        )
        
    def compare_scenarios(self):
        """Navigate to scenarios comparison page."""
        if self.parent:
            self.parent.navigate_to_page(4)  # Navigate to the comparison page

    def import_scenario(self):
        """Import scenario from external file."""
        dialog = ImportScenarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            imported_scenario = dialog.get_imported_scenario()
            if imported_scenario:
                # Add the scenario
                self.add_new_scenario(imported_scenario)
                
                # Force UI update before showing message
                self.update_ui_state()
                
                # Process any pending events to ensure UI is fully updated
                QCoreApplication.processEvents()
                
                # Now show the success message
                QMessageBox.information(
                    self, "Import Successful",
                    f"Scenario '{imported_scenario.name}' has been imported successfully."
                )
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        for tab_page in self.scenario_tabs.values():
            tab_page.refresh_product_data()

    def export(self):
        """Export functionality placeholder."""
        QMessageBox.information(
            self, "Coming Soon", 
            "Export functionality will be developed in a future update."
        )