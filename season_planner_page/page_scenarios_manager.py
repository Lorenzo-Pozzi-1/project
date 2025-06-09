"""
Scenarios Manager Page for the Season Planner.

Main interface for managing multiple pesticide application scenarios
using the new table-based interface.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, QMessageBox, QInputDialog, QDialog
from PySide6.QtCore import QCoreApplication, Signal

from common import (
    ContentFrame, HeaderWithHomeButton, calculation_tracer, create_button, 
    ScoreBar, get_margin_large, get_spacing_medium, get_subtitle_font
)
from season_planner_page.tab_scenario import ScenarioTabPage
from season_planner_page.import_export import ImportScenarioDialog
from data import Scenario


class ScenariosManagerPage(QWidget):
    """
    Container for multiple scenario tabs with management functionality.
    
    This page serves as the main interface for the Season Planner feature,
    using the new table-based applications interface for better performance
    and user experience.
    """
    
    scenario_changed = Signal(object)  # Emitted when any scenario changes
    
    def __init__(self, parent=None):
        """Initialize the scenarios manager page."""
        super().__init__(parent)
        self.parent = parent
        self._scenarios = []  # Internal list of scenarios
        self._tab_pages = {}  # Map scenario name to tab page
        self._ui_components = {}  # Store UI components for easy access
        
        self._setup_ui()
        self._create_default_scenario()
        calculation_tracer.clear()
    
    # Properties for cleaner data access
    @property
    def scenarios(self):
        """Get list of all scenarios."""
        return self._scenarios.copy()
    
    @property
    def current_scenario(self):
        """Get the currently selected scenario."""
        current_page = self._get_current_page()
        return current_page.get_scenario() if current_page else None
    
    @property
    def current_page(self):
        """Get the currently selected scenario page."""
        return self._get_current_page()
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        # Header with navigation and action buttons
        main_layout.addWidget(self._create_header())
        
        # Tab widget for scenarios
        main_layout.addWidget(self._create_tab_widget())
        
        # EIQ results display
        main_layout.addWidget(self._create_results_display())
    
    def _create_header(self):
        """Create the header with navigation and action buttons."""
        header = HeaderWithHomeButton("Season Planner - Scenarios")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Action buttons
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        button_configs = [
            ("Import Scenario", "white", self.import_scenario),
            ("New Scenario", "yellow", self.add_scenario),
            ("Clone Current", "white", self.clone_scenario),
            ("Rename", "white", self.rename_scenario),
            ("Delete", "white", self.delete_scenario),
            ("Compare Scenarios", "yellow", self.compare_scenarios),
            ("Export", "special", self.export)
        ]
        
        self._ui_components['buttons'] = {}
        for text, style, callback in button_configs:
            btn = create_button(text, style=style, callback=callback, parent=self)
            buttons_layout.addWidget(btn)
            self._ui_components['buttons'][text] = btn
        
        buttons_frame.layout.addLayout(buttons_layout)
        header.layout().addWidget(buttons_frame)
        
        return header
    
    def _create_tab_widget(self):
        """Create the tab widget for scenarios."""
        tabs_frame = ContentFrame()
        tabs_layout = QVBoxLayout()
        
        self._ui_components['tab_widget'] = QTabWidget()
        self._ui_components['tab_widget'].setMovable(True)
        self._ui_components['tab_widget'].currentChanged.connect(self._on_tab_changed)
        self._ui_components['tab_widget'].tabBarClicked.connect(self._on_tab_moved)
        
        tabs_layout.addWidget(self._ui_components['tab_widget'])
        tabs_frame.layout.addLayout(tabs_layout)
        
        return tabs_frame
    
    def _create_results_display(self):
        """Create the EIQ results display section."""
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Scenario info title
        self._ui_components['info_title'] = QLabel(
            "New Scenario: 0 applications | Field Use EIQ: 0.00", 
            font=get_subtitle_font()
        )
        results_layout.addWidget(self._ui_components['info_title'])
        
        # EIQ score bar
        self._ui_components['score_bar'] = ScoreBar(preset="regen_ag")
        self._ui_components['score_bar'].set_value(0, "No applications")
        results_layout.addWidget(self._ui_components['score_bar'])
        
        results_frame.layout.addLayout(results_layout)
        return results_frame
    
    def _create_default_scenario(self):
        """Create the initial default scenario."""
        scenario = Scenario("Scenario 1")
        self._add_scenario_internal(scenario)
    
    def _generate_unique_name(self, base_name):
        """Generate a unique scenario name."""
        if base_name not in self._tab_pages:
            return base_name
        
        counter = 1
        while f"{base_name} ({counter})" in self._tab_pages:
            counter += 1
        
        return f"{base_name} ({counter})"
    
    def _validate_scenario_name(self, name, exclude_current=False):
        """Validate that a scenario name is unique."""
        current_scenario = self.current_scenario if exclude_current else None
        
        for scenario in self._scenarios:
            if scenario.name == name and scenario != current_scenario:
                return False
        return True
    
    def _add_scenario_internal(self, scenario):
        """Internal method to add a scenario without validation."""
        # Ensure unique name
        scenario.name = self._generate_unique_name(scenario.name)
        
        # Create tab page
        tab_page = ScenarioTabPage(self, scenario)
        tab_page.scenario_changed.connect(self._on_scenario_data_changed)
        
        # Add to UI
        tab_index = self._ui_components['tab_widget'].addTab(tab_page, scenario.name)
        self._ui_components['tab_widget'].setCurrentIndex(tab_index)
        
        # Update internal data
        self._scenarios.append(scenario)
        self._tab_pages[scenario.name] = tab_page
        
        self._update_ui_state()
        return tab_page
    
    def _remove_scenario_internal(self, scenario):
        """Internal method to remove a scenario."""
        # Find and remove tab
        for i in range(self._ui_components['tab_widget'].count()):
            page = self._ui_components['tab_widget'].widget(i)
            if page.get_scenario() is scenario:
                self._ui_components['tab_widget'].removeTab(i)
                break
        
        # Update internal data
        self._scenarios.remove(scenario)
        del self._tab_pages[scenario.name]
        
        self._update_ui_state()
    
    def _get_current_page(self):
        """Get the current scenario page."""
        index = self._ui_components['tab_widget'].currentIndex()
        if index < 0:
            return None
        return self._ui_components['tab_widget'].widget(index)
    
    def _update_ui_state(self):
        """Update all UI components based on current state."""
        self._update_button_states()
        self._update_results_display()
    
    def _update_button_states(self):
        """Update button enabled/disabled states."""
        has_scenarios = len(self._scenarios) > 0
        buttons = self._ui_components['buttons']
        
        buttons["Clone Current"].setEnabled(has_scenarios)
        buttons["Rename"].setEnabled(has_scenarios)
        buttons["Delete"].setEnabled(has_scenarios)
        buttons["Compare Scenarios"].setEnabled(len(self._scenarios) > 1)
        buttons["Export"].setEnabled(has_scenarios)
    
    def _update_results_display(self):
        """Update the EIQ results display."""
        current_page = self._get_current_page()
        
        if not current_page:
            scenario_name = "No scenario selected"
            total_eiq = 0.0
            applications_count = 0
        else:
            scenario = current_page.get_scenario()
            scenario_name = scenario.name
            total_eiq = current_page.get_total_field_eiq()
            applications = current_page.applications_table.get_applications()
            applications_count = len(applications)
        
        # Update display
        info_text = f"{scenario_name}: {applications_count} applications | Field Use EIQ: {total_eiq:.2f}"
        self._ui_components['info_title'].setText(info_text)
        
        score_text = "" if total_eiq > 0 else "No applications"
        self._ui_components['score_bar'].set_value(max(total_eiq, 0), score_text)
    
    def _is_scenario_empty(self, scenario):
        """Check if a scenario has no meaningful applications."""
        if not scenario.applications:
            return True
        
        return all(
            not (app.product_name and app.product_name.strip())
            for app in scenario.applications
        )
    
    def _remove_empty_placeholder_if_needed(self):
        """Remove empty placeholder scenario if it's the only one."""
        if len(self._scenarios) == 1 and self._is_scenario_empty(self._scenarios[0]):
            self._remove_scenario_internal(self._scenarios[0])
    
    def _sync_tab_order(self):
        """Synchronize internal data with tab widget order."""
        new_scenarios = []
        new_tab_pages = {}
        
        for i in range(self._ui_components['tab_widget'].count()):
            tab_page = self._ui_components['tab_widget'].widget(i)
            scenario = tab_page.get_scenario()
            new_scenarios.append(scenario)
            new_tab_pages[scenario.name] = tab_page
        
        self._scenarios = new_scenarios
        self._tab_pages = new_tab_pages
    
    # Event handlers
    def _on_tab_changed(self):
        """Handle tab selection change."""
        self._update_ui_state()
    
    def _on_tab_moved(self, index):
        """Handle tab reordering."""
        self._sync_tab_order()
    
    def _on_scenario_data_changed(self, scenario):
        """Handle changes to scenario data."""
        # Find the tab page and update tab text if name changed
        for i in range(self._ui_components['tab_widget'].count()):
            page = self._ui_components['tab_widget'].widget(i)
            if page.get_scenario() is scenario:
                current_tab_text = self._ui_components['tab_widget'].tabText(i)
                
                if current_tab_text != scenario.name:
                    # Validate name uniqueness
                    if not self._validate_scenario_name(scenario.name, exclude_current=True):
                        QMessageBox.warning(
                            self, "Name Already Exists",
                            "Scenario names must be unique. Reverting to previous name.",
                            QMessageBox.Ok
                        )
                        scenario.name = current_tab_text
                    else:
                        # Update tab and internal mapping
                        self._ui_components['tab_widget'].setTabText(i, scenario.name)
                        del self._tab_pages[current_tab_text]
                        self._tab_pages[scenario.name] = page
                break
        
        self._update_ui_state()
        self.scenario_changed.emit(scenario)
    
    # Public API methods
    def add_scenario(self, scenario=None):
        """Add a new scenario."""
        if scenario is None:
            base_name = f"Scenario {len(self._scenarios) + 1}"
            scenario = Scenario(base_name)
        
        self._add_scenario_internal(scenario)
    
    def clone_scenario(self):
        """Clone the current scenario."""
        current_page = self._get_current_page()
        if current_page:
            original_scenario = current_page.get_scenario()
            cloned_scenario = original_scenario.clone()
            self._add_scenario_internal(cloned_scenario)
    
    def rename_scenario(self):
        """Rename the current scenario."""
        current_page = self._get_current_page()
        if not current_page:
            return
        
        scenario = current_page.get_scenario()
        old_name = scenario.name
        
        while True:
            new_name, ok = QInputDialog.getText(
                self, "Rename Scenario", "Enter new scenario name:",
                text=old_name
            )
            
            if not ok or new_name == old_name:
                return
            
            if not new_name.strip():
                QMessageBox.warning(
                    self, "Invalid Name",
                    "Scenario name cannot be empty.",
                    QMessageBox.Ok
                )
                continue
            
            if not self._validate_scenario_name(new_name, exclude_current=True):
                QMessageBox.warning(
                    self, "Name Already Exists",
                    "Scenario names must be unique.",
                    QMessageBox.Ok
                )
                continue
            
            # Valid name - update
            scenario.name = new_name
            current_index = self._ui_components['tab_widget'].currentIndex()
            self._ui_components['tab_widget'].setTabText(current_index, new_name)
            
            # Update internal mapping
            del self._tab_pages[old_name]
            self._tab_pages[new_name] = current_page
            
            self._update_ui_state()
            break
    
    def delete_scenario(self):
        """Delete the current scenario with confirmation."""
        current_page = self._get_current_page()
        if not current_page:
            return
        
        scenario = current_page.get_scenario()
        
        result = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove scenario '{scenario.name}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self._remove_scenario_internal(scenario)
            
            # Ensure we always have at least one scenario
            if len(self._scenarios) == 0:
                self._create_default_scenario()
    
    def import_scenario(self):
        """Import scenario from external file."""
        dialog = ImportScenarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            imported_scenario = dialog.get_imported_scenario()
            if imported_scenario:
                self._remove_empty_placeholder_if_needed()
                self._add_scenario_internal(imported_scenario)
                
                # Force UI update before showing message
                QCoreApplication.processEvents()
                
                QMessageBox.information(
                    self, "Import Successful",
                    f"Scenario '{imported_scenario.name}' has been imported successfully."
                )
    
    def export(self):
        """Export functionality placeholder."""
        QMessageBox.information(
            self, "Coming Soon",
            "Export functionality will be added here."
        )
    
    def compare_scenarios(self):
        """Navigate to scenarios comparison page."""
        if self.parent:
            self.parent.navigate_to_page(4)
    
    def refresh_product_data(self):
        """Refresh product data in all scenario tabs."""
        for tab_page in self._tab_pages.values():
            tab_page.refresh_product_data()