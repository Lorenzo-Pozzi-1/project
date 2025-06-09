"""
Scenarios Manager Page for the Season Planner.

Main interface for managing multiple pesticide application scenarios.
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


class ScenarioValidator:
    """Handles scenario validation logic."""
    
    @staticmethod
    def validate_name(name, existing_scenarios, exclude_scenario=None):
        """
        Validate scenario name uniqueness.
        Returns: (is_valid: bool, error_message: str)
        """
        name = name.strip()
        if not name:
            return False, "Scenario name cannot be empty"
        
        # Check for name conflicts, excluding current scenario being renamed
        for scenario in existing_scenarios:
            if scenario.name == name and scenario != exclude_scenario:
                return False, "Scenario name must be unique"
        
        return True, ""
    
    @staticmethod
    def generate_unique_name(base_name, existing_scenarios):
        """Generate unique scenario name by appending counter if needed."""
        if not any(s.name == base_name for s in existing_scenarios):
            return base_name
        
        # Find next available number suffix
        counter = 1
        while any(s.name == f"{base_name} ({counter})" for s in existing_scenarios):
            counter += 1
        
        return f"{base_name} ({counter})"
    
    @staticmethod
    def is_scenario_empty(scenario):
        """Check if scenario has meaningful applications (non-empty product names)."""
        if not scenario.applications:
            return True
        
        return all(
            not (app.product_name and app.product_name.strip())
            for app in scenario.applications
        )


class ScenariosManagerPage(QWidget):
    """
    Container for multiple scenario tabs with management functionality.
    
    This page serves as the main interface for the Season Planner feature.
    """
    
    scenario_changed = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self._scenarios = []  # List of Scenario objects
        self._tab_pages = {}  # Map scenario names to ScenarioTabPage instances
        
        # UI components - initialized in _setup_ui()
        self._tab_widget = None
        self._buttons = {}
        self._info_title = None
        self._score_bar = None
        
        self._setup_ui()
        self._create_default_scenario()  # Start with one empty scenario
        calculation_tracer.clear()
    
    # === PROPERTIES ===
    @property
    def scenarios(self):
        """Return copy of scenarios list to prevent external modification."""
        return self._scenarios.copy()
    
    @property
    def current_scenario(self):
        """Get scenario object from currently selected tab."""
        current_page = self._get_current_page()
        return current_page.get_scenario() if current_page else None
    
    @property
    def current_page(self):
        """Get currently active ScenarioTabPage widget."""
        return self._get_current_page()
    
    # === UI SETUP ===
    def _setup_ui(self):
        """Create main layout with header, tabs, and results display."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_medium())
        
        main_layout.addWidget(self._create_header())
        main_layout.addWidget(self._create_tab_widget())
        main_layout.addWidget(self._create_results_display())
    
    def _create_header(self):
        """Create header with title and action buttons."""
        header = HeaderWithHomeButton("Season Planner - Scenarios")
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Container for all action buttons
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        # Define button configuration: (text, style, callback)
        button_configs = [
            ("Import Scenario", "white", self.import_scenario),
            ("New Scenario", "yellow", self.add_scenario),
            ("Clone Current", "white", self.clone_scenario),
            ("Rename", "white", self.rename_scenario),
            ("Delete", "white", self.delete_scenario),
            ("Compare Scenarios", "yellow", self.compare_scenarios),
            ("Export", "special", self.export)
        ]
        
        # Create and store buttons for later state management
        for text, style, callback in button_configs:
            btn = create_button(text, style=style, callback=callback, parent=self)
            buttons_layout.addWidget(btn)
            self._buttons[text] = btn
        
        buttons_frame.layout.addLayout(buttons_layout)
        header.layout().addWidget(buttons_frame)
        return header
    
    def _create_tab_widget(self):
        """Create container for scenario tabs with drag-and-drop support."""
        tabs_frame = ContentFrame()
        tabs_layout = QVBoxLayout()
        
        self._tab_widget = QTabWidget()
        self._tab_widget.setMovable(True)  # Allow tab reordering
        self._tab_widget.currentChanged.connect(self._on_tab_changed)
        self._tab_widget.tabBarClicked.connect(self._on_tab_moved)
        
        tabs_layout.addWidget(self._tab_widget)
        tabs_frame.layout.addLayout(tabs_layout)
        return tabs_frame
    
    def _create_results_display(self):
        """Create EIQ score display at bottom of page."""
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Summary text showing scenario name, application count, and total EIQ
        self._info_title = QLabel(
            "New Scenario: 0 applications | Field Use EIQ: 0.00", 
            font=get_subtitle_font()
        )
        results_layout.addWidget(self._info_title)
        
        # Visual EIQ score bar
        self._score_bar = ScoreBar(preset="regen_ag")
        self._score_bar.set_value(0, "No applications")
        results_layout.addWidget(self._score_bar)
        
        results_frame.layout.addLayout(results_layout)
        return results_frame
    
    # === SCENARIO MANAGEMENT ===
    def _create_default_scenario(self):
        """Create initial empty scenario on startup."""
        scenario = Scenario("Scenario 1")
        self._add_scenario_internal(scenario)
    
    def _add_scenario_internal(self, scenario):
        """Add scenario to UI and internal data structures."""
        # Ensure unique name to prevent conflicts
        scenario.name = ScenarioValidator.generate_unique_name(scenario.name, self._scenarios)
        
        # Create corresponding tab page widget
        tab_page = ScenarioTabPage(self, scenario)
        tab_page.scenario_changed.connect(self._on_scenario_data_changed)
        
        # Add tab to UI and make it active
        tab_index = self._tab_widget.addTab(tab_page, scenario.name)
        self._tab_widget.setCurrentIndex(tab_index)
        
        # Update internal data structures
        self._scenarios.append(scenario)
        self._tab_pages[scenario.name] = tab_page
        
        self._update_ui_state()
        return tab_page
    
    def _remove_scenario_internal(self, scenario):
        """Remove scenario from UI and internal data structures."""
        # Find and remove corresponding tab
        for i in range(self._tab_widget.count()):
            page = self._tab_widget.widget(i)
            if page.get_scenario() is scenario:
                self._tab_widget.removeTab(i)
                break
        
        # Clean up internal data
        self._scenarios.remove(scenario)
        del self._tab_pages[scenario.name]
        self._update_ui_state()
    
    def _get_current_page(self):
        """Get currently active tab page widget."""
        index = self._tab_widget.currentIndex()
        return self._tab_widget.widget(index) if index >= 0 else None
    
    def _remove_empty_placeholder_if_needed(self):
        """Remove default empty scenario when importing/adding real scenarios."""
        if len(self._scenarios) == 1 and ScenarioValidator.is_scenario_empty(self._scenarios[0]):
            self._remove_scenario_internal(self._scenarios[0])
    
    def _sync_tab_order(self):
        """Synchronize internal data with tab widget order after drag-and-drop."""
        new_scenarios = []
        new_tab_pages = {}
        
        # Rebuild data structures based on current tab order
        for i in range(self._tab_widget.count()):
            tab_page = self._tab_widget.widget(i)
            scenario = tab_page.get_scenario()
            new_scenarios.append(scenario)
            new_tab_pages[scenario.name] = tab_page
        
        self._scenarios = new_scenarios
        self._tab_pages = new_tab_pages
    
    # === UI STATE MANAGEMENT ===
    def _update_ui_state(self):
        """Refresh button states and results display based on current state."""
        self._update_button_states()
        self._update_results_display()
    
    def _update_button_states(self):
        """Enable/disable buttons based on number of scenarios and current state."""
        has_scenarios = len(self._scenarios) > 0
        self._buttons["Clone Current"].setEnabled(has_scenarios)
        self._buttons["Rename"].setEnabled(has_scenarios)
        self._buttons["Delete"].setEnabled(has_scenarios)
        self._buttons["Compare Scenarios"].setEnabled(len(self._scenarios) > 1)  # Need 2+ scenarios
        self._buttons["Export"].setEnabled(has_scenarios)
    
    def _update_results_display(self):
        """Update EIQ summary display with current scenario data."""
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
        
        # Update summary text
        info_text = f"{scenario_name}: {applications_count} applications | Field Use EIQ: {total_eiq:.2f}"
        self._info_title.setText(info_text)
        
        # Update visual score bar
        score_text = "" if total_eiq > 0 else "No applications"
        self._score_bar.set_value(max(total_eiq, 0), score_text)
    
    # === EVENT HANDLERS ===
    def _on_tab_changed(self):
        """Handle tab selection change - update UI state."""
        self._update_ui_state()
    
    def _on_tab_moved(self, index):
        """Handle tab drag-and-drop - synchronize internal data."""
        self._sync_tab_order()
    
    def _on_scenario_data_changed(self, scenario):
        """Handle scenario modification - validate names and update UI."""
        # Handle name changes with validation
        for i in range(self._tab_widget.count()):
            page = self._tab_widget.widget(i)
            if page.get_scenario() is scenario:
                current_tab_text = self._tab_widget.tabText(i)
                
                # Check if scenario name was changed
                if current_tab_text != scenario.name:
                    is_valid, error_msg = ScenarioValidator.validate_name(
                        scenario.name, self._scenarios, exclude_scenario=scenario
                    )
                    
                    if not is_valid:
                        # Revert to old name if validation fails
                        QMessageBox.warning(self, "Name Already Exists", error_msg, QMessageBox.Ok)
                        scenario.name = current_tab_text
                    else:
                        # Update tab text and internal mapping
                        self._tab_widget.setTabText(i, scenario.name)
                        del self._tab_pages[current_tab_text]
                        self._tab_pages[scenario.name] = page
                break
        
        self._update_ui_state()
        self.scenario_changed.emit(scenario)
    
    # === PUBLIC API ===
    def add_scenario(self, scenario=None):
        """Add new scenario or create default one."""
        if scenario is None:
            base_name = f"Scenario {len(self._scenarios) + 1}"
            scenario = Scenario(base_name)
        
        self._add_scenario_internal(scenario)
    
    def clone_scenario(self):
        """Create copy of currently selected scenario."""
        current_page = self._get_current_page()
        if current_page:
            original_scenario = current_page.get_scenario()
            cloned_scenario = original_scenario.clone()
            self._add_scenario_internal(cloned_scenario)
    
    def rename_scenario(self):
        """Show dialog to rename current scenario with validation."""
        current_page = self._get_current_page()
        if not current_page:
            return
        
        scenario = current_page.get_scenario()
        old_name = scenario.name
        
        # Keep asking until valid name or cancelled
        while True:
            new_name, ok = QInputDialog.getText(
                self, "Rename Scenario", "Enter new scenario name:", text=old_name
            )
            
            if not ok or new_name == old_name:
                return
            
            # Validate new name
            is_valid, error_msg = ScenarioValidator.validate_name(
                new_name, self._scenarios, exclude_scenario=scenario
            )
            
            if not is_valid:
                QMessageBox.warning(self, "Invalid Name", error_msg, QMessageBox.Ok)
                continue
            
            # Apply name change
            scenario.name = new_name
            current_index = self._tab_widget.currentIndex()
            self._tab_widget.setTabText(current_index, new_name)
            
            # Update internal mapping
            del self._tab_pages[old_name]
            self._tab_pages[new_name] = current_page
            
            self._update_ui_state()
            break
    
    def delete_scenario(self):
        """Delete current scenario with confirmation dialog."""
        current_page = self._get_current_page()
        if not current_page:
            return
        
        scenario = current_page.get_scenario()
        
        # Confirm deletion
        result = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove scenario '{scenario.name}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self._remove_scenario_internal(scenario)
            
            # Ensure at least one scenario exists
            if len(self._scenarios) == 0:
                self._create_default_scenario()
    
    def import_scenario(self):
        """Show import dialog and add imported scenario."""
        dialog = ImportScenarioDialog(self)
        if dialog.exec() == QDialog.Accepted:
            imported_scenario = dialog.get_imported_scenario()
            if imported_scenario:
                # Remove empty placeholder scenario if present
                self._remove_empty_placeholder_if_needed()
                self._add_scenario_internal(imported_scenario)
                
                # Process UI events before showing success message
                QCoreApplication.processEvents()
                
                QMessageBox.information(
                    self, "Import Successful",
                    f"Scenario '{imported_scenario.name}' has been imported successfully."
                )
    
    def export(self):
        """Placeholder for export functionality."""
        QMessageBox.information(self, "Coming Soon", "Export functionality will be added here.")
    
    def compare_scenarios(self):
        """Navigate to scenario comparison page."""
        if self.parent:
            self.parent.navigate_to_page(4)
    
    def refresh_product_data(self):
        """Refresh product data in all scenario tabs (called when product database updates)."""
        for tab_page in self._tab_pages.values():
            tab_page.refresh_product_data()