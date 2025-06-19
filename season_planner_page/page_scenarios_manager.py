"""
Scenarios Manager Page for the Season Planner.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QMessageBox, QInputDialog, QDialog, QTabBar
)
from PySide6.QtCore import QCoreApplication, Signal

from common.constants import get_margin_large, get_spacing_medium
from common.styles import get_subtitle_font
from common.widgets.header_frame_buttons import ContentFrame, HeaderWithHomeButton, create_button
from common.widgets.scorebar import ScoreBar
from common.widgets.tracer import calculation_tracer
from season_planner_page.import_export.exporter import ExcelScenarioExporter
from season_planner_page.tab_scenario import ScenarioTabPage
from season_planner_page.import_export.import_dialog import ImportScenarioDialog
from data.model_scenario import Scenario


class CustomTabBar(QTabBar):
    """Custom tab bar that emits a signal to be renamed when double-clicked."""
    
    tab_double_clicked = Signal(int)  # Signal emitted with the tab index
    
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events on tabs."""
        for i in range(self.count()):
            if self.tabRect(i).contains(event.pos()):
                self.tab_double_clicked.emit(i)
                break
        
        super().mouseDoubleClickEvent(event)
    


class ScenariosManagerPage(QWidget):
    """
    container for multiple scenario tabs with management functionality.
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
        main_layout.setContentsMargins(
            get_margin_large(), get_margin_large(), 
            get_margin_large(), get_margin_large()
        )
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with back button and operation buttons
        header = HeaderWithHomeButton("Season Planner - Scenarios")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Wrap buttons in ContentFrame
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        # Create buttons
        buttons = {
            "Import Scenario": ("white", self.import_scenario),
            "New Scenario": ("yellow", self.add_new_scenario),
            "Clone Current": ("white", self.clone_current_scenario),
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
        
        # Tab widget for scenarios with custom tab bar
        self.tab_widget = QTabWidget()
        self.custom_tab_bar = CustomTabBar()
        self.tab_widget.setTabBar(self.custom_tab_bar)
        
        self.tab_widget.setMovable(True)  # Enable drag-to-reorder
        self.tab_widget.currentChanged.connect(self.update_ui_state)
        self.tab_widget.tabBarClicked.connect(self._on_tab_moved)  # Handle reordering
        
        # Connect double-click signal to rename function
        self.custom_tab_bar.tab_double_clicked.connect(self._on_tab_double_clicked)
        
        tabs_layout.addWidget(self.tab_widget)
        tabs_frame.layout.addLayout(tabs_layout)
        main_layout.addWidget(tabs_frame)
        
        # EIQ Results Display
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()

        # Combined title with scenario info
        self.scenario_info_title = QLabel(
            "New Scenario: 0 applications | Field Use EIQ: 0.00", 
            font=get_subtitle_font()
        )
        results_layout.addWidget(self.scenario_info_title)

        # Create score bar with custom thresholds and labels
        self.eiq_score_bar = ScoreBar(preset="regen_ag")
        self.eiq_score_bar.set_value(0, "No applications")
        results_layout.addWidget(self.eiq_score_bar)

        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def _on_tab_double_clicked(self, tab_index):
        """Handle double-click on a tab to trigger rename."""
        self.tab_widget.setCurrentIndex(tab_index)
        self.rename_current_scenario()
    
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
            # Ensure cloned/imported scenario has a unique name
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
            
            # update tab text
            self.tab_widget.setTabText(index, new_name)
            
            # Update dictionary
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
            f"Are you sure you want to remove this scenario?\n\n'{scenario.name}'",
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
        self.action_buttons["Delete"].setEnabled(has_tabs)
        
        # Update EIQ display
        page, _ = self.get_current_scenario_page()
        if not page:
            scenario_name = "No scenario selected"
            total_eiq = 0.0
            applications_count = 0
            validation_status = ""
        else:
            scenario_name = page.get_scenario().name
            total_eiq = page.get_total_field_eiq()
            applications_count = page.get_applications_count()
            
            # Add validation status
            if page.has_validation_issues():
                validation_status = " (⚠ There are invalid or incomplete applications!)"
            else:
                validation_status = ""
        
        # Update combined title
        self.scenario_info_title.setText(
            f"{scenario_name}: {applications_count} applications | "
            f"Field Use EIQ: {total_eiq:.2f}{validation_status}"
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
        """Import scenario from external file using dialog."""
        dialog = ImportScenarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            imported_scenario = dialog.get_imported_scenario()
            if imported_scenario:
                # Check if we should remove the empty placeholder scenario
                self._remove_empty_placeholder_if_needed()
                
                # FIXED: Don't use clone() which adds "Copy of" prefix
                # Just ensure the name is unique without adding "Copy of"
                original_name = imported_scenario.name
                imported_scenario.name = self.generate_unique_name(original_name)
                
                # Add the scenario
                self.add_new_scenario(imported_scenario)
                
                # Force UI update before showing message
                self.update_ui_state()
                
                # Process any pending events to ensure UI is fully updated
                QCoreApplication.processEvents()
                
                # Show success message with import summary
                apps_count = len(imported_scenario.applications) if imported_scenario.applications else 0
                QMessageBox.information(
                    self, "Import Successful",
                    f"Scenario '{imported_scenario.name}' imported successfully!\n\n"
                    f"Applications imported: {apps_count}\n"
                    f"Ready for review and editing."
                )
    
    def _remove_empty_placeholder_if_needed(self):
        """Remove the empty placeholder scenario if it's the only one and is empty."""
        # Only proceed if there's exactly one scenario
        if len(self.scenarios) != 1:
            return
            
        # Get the single scenario
        scenario = self.scenarios[0]
        
        # Check if it's an empty placeholder
        if self._is_scenario_empty(scenario):
            # Find the tab page and remove it
            for i in range(self.tab_widget.count()):
                page = self.tab_widget.widget(i)
                if page.get_scenario() is scenario:
                    # Remove the tab
                    self.tab_widget.removeTab(i)
                    # Remove from our data structures
                    self.scenarios.remove(scenario)
                    del self.scenario_tabs[scenario.name]
                    break
    
    def _is_scenario_empty(self, scenario):
        """Check if a scenario is empty (no meaningful applications)."""
        # If no applications at all, it's empty
        if not scenario.applications:
            return True
            
        # Check if all applications are empty (no product name)
        for app in scenario.applications:
            if app.product_name and app.product_name.strip():
                return False  # Found at least one application with a product
                
        return True  # All applications are empty

    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        for tab_page in self.scenario_tabs.values():
            tab_page.refresh_product_data()

    def export(self):
        """Export all scenarios to Excel file."""
        if not self.scenarios:
            QMessageBox.information(
                self, "No Scenarios", 
                "There are no scenarios to export."
            )
            return
        
        # Filter out empty scenarios
        scenarios_to_export = []
        for scenario in self.scenarios:
            if not self._is_scenario_empty(scenario):
                scenarios_to_export.append(scenario)
        
        if not scenarios_to_export:
            QMessageBox.information(
                self, "No Data to Export", 
                "All scenarios are empty. Add some applications before exporting."
            )
            return
        
        # Export using the existing exporter
        try:
            exporter = ExcelScenarioExporter()
            exporter.export_scenarios(scenarios_to_export, self)
            
        except ImportError as e:
            QMessageBox.critical(
                self, "Export Error",
                f"Export functionality is not available. Missing required library: {e}"
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", 
                f"An unexpected error occurred during export: {e}"
            )

    def _on_tab_moved(self, index):
        """Handle tab reordering to keep internal data structures in sync."""
        # Rebuild the scenarios list to match the new tab order
        new_scenarios = []
        new_scenario_tabs = {}
        
        for i in range(self.tab_widget.count()):
            tab_page = self.tab_widget.widget(i)
            scenario = tab_page.get_scenario()
            new_scenarios.append(scenario)
            new_scenario_tabs[scenario.name] = tab_page
        
        # Update our data structures
        self.scenarios = new_scenarios
        self.scenario_tabs = new_scenario_tabs