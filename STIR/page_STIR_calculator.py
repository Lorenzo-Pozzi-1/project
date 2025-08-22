"""
STIR Calculator page

This module defines the STIRCalculatorPage class which provides a
tabbed interface for managing STIR scenarios similar to the EIQ season planner.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTabWidget, 
    QMessageBox, QInputDialog, QTabBar, QComboBox
)
from PySide6.QtCore import Qt, Signal

from common.constants import get_margin_large, get_spacing_medium
from common.styles import get_subtitle_font
from common.widgets.header_frame_buttons import ContentFrame, create_button, HeaderWithHomeButton
from common.widgets.scorebar import ScoreBar
from .tab_scenario import STIRScenarioTabPage
from common.utils import set_preference, get_preference


class CustomSTIRTabBar(QTabBar):
    """Custom tab bar for STIR scenarios with double-click to rename."""
    
    tab_double_clicked = Signal(int)  # Signal emitted with the tab index
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def mouseDoubleClickEvent(self, event):
        """Handle double-click events on tabs."""
        for i in range(self.count()):
            if self.tabRect(i).contains(event.pos()):
                self.tab_double_clicked.emit(i)
                break
        
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
        self.scenario_tabs = {}
        
        # Load STIR preferences
        self.depth_uom = get_preference("STIR_preferences", "default_depth_uom", "inch")
        self.speed_uom = get_preference("STIR_preferences", "default_speed_uom", "mph")
        
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
        header.back_clicked.connect(lambda: self.parent.navigate_to_page(0))
        
        # Wrap action buttons in ContentFrame
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        
        # Add custom machine management button
        manage_button = create_button(text="My machines", style='white', 
                                    callback=self.open_custom_machine_manager)
        buttons_layout.addWidget(manage_button)
        
        # Add separator
        separator1 = QLabel("|")
        separator1.setStyleSheet("color: #ccc; font-size: 16px; margin: 0 10px;")
        buttons_layout.addWidget(separator1)
        
        # Add UOM selection controls
        uom_layout = QHBoxLayout()

        # Depth UOM selector
        depth_label = QLabel("Depth:")
        self.depth_uom_combo = QComboBox()
        self.depth_uom_combo.addItems(["inch", "cm"])
        self.depth_uom_combo.setCurrentText(self.depth_uom)
        self.depth_uom_combo.currentTextChanged.connect(self.on_depth_uom_changed)
        
        # Speed UOM selector
        speed_label = QLabel("Speed:")
        self.speed_uom_combo = QComboBox()
        self.speed_uom_combo.addItems(["mph", "km/h"])
        self.speed_uom_combo.setCurrentText(self.speed_uom)
        self.speed_uom_combo.currentTextChanged.connect(self.on_speed_uom_changed)
        
        uom_layout.addWidget(depth_label)
        uom_layout.addWidget(self.depth_uom_combo)
        uom_layout.addWidget(speed_label)
        uom_layout.addWidget(self.speed_uom_combo)
        
        buttons_layout.addLayout(uom_layout)
        
        # Add separator
        separator = QLabel("|")
        separator.setStyleSheet("color: #ccc; font-size: 16px; margin: 0 10px;")
        buttons_layout.addWidget(separator)
        
        # Create action buttons
        buttons = {
            "New Scenario": ("yellow", self.new_scenario),
            "Clone Current": ("white", self.clone_current_scenario),
            "Delete": ("white", self.delete_current_scenario),
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
        self.tab_widget.tabBarClicked.connect(self._on_tab_moved)
        
        # Connect double-click signal to rename function
        self.custom_tab_bar.tab_double_clicked.connect(self._on_tab_double_clicked)
        
        tabs_layout.addWidget(self.tab_widget)
        tabs_frame.layout.addLayout(tabs_layout)
        main_layout.addWidget(tabs_frame)
        
        # Results Display
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Combined title with scenario info
        self.scenario_info_title = QLabel(
            "Scenario 1: 6 operations | Total STIR: 268", 
            font=get_subtitle_font()
        )
        results_layout.addWidget(self.scenario_info_title)
        
        # Create score bar for STIR intensity using the new "stir" preset
        self.stir_score_bar = ScoreBar(preset="stir")
        self.stir_score_bar.set_value(268, "Intense")
        results_layout.addWidget(self.stir_score_bar)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def on_depth_uom_changed(self, new_uom):
        """Handle depth UOM change."""
        self.depth_uom = new_uom
        # Auto-save STIR preferences (less critical, for convenience)
        set_preference("STIR_preferences", "default_depth_uom", new_uom, auto_save=True)
        self.update_all_scenarios_uom()

    def on_speed_uom_changed(self, new_uom):
        """Handle speed UOM change."""
        self.speed_uom = new_uom
        # Auto-save STIR preferences (less critical, for convenience)
        set_preference("STIR_preferences", "default_speed_uom", new_uom, auto_save=True)
        self.update_all_scenarios_uom()

    def _save_stir_preferences(self):
        """Save STIR preferences to config. (DEPRECATED - now auto-saved)"""
        # This method is kept for backward compatibility but no longer needed
        # since STIR preferences are now auto-saved in the UOM change handlers
        pass
    
    def update_all_scenarios_uom(self):
        """Update UOM settings for all scenarios."""
        for scenario_page in self.scenario_tabs.values():
            scenario_page.set_display_uom(self.depth_uom, self.speed_uom)
    
    def get_current_uom_settings(self):
        """Get current UOM settings."""
        return {
            'depth_uom': self.depth_uom,
            'speed_uom': self.speed_uom
        }
    
    def add_initial_scenarios(self):
        """Add initial scenario."""
        # Add one initial scenario
        scenario1 = STIRScenarioTabPage(self, "New Scenario")
        scenario1.scenario_changed.connect(self.on_scenario_changed)
        
        # Set initial UOM settings
        scenario1.set_display_uom(self.depth_uom, self.speed_uom)

        self.tab_widget.addTab(scenario1, "New Scenario")
        self.scenario_tabs["New Scenario"] = scenario1

        # Set the first tab as current
        self.tab_widget.setCurrentIndex(0)
        self.update_ui_state()
    
    def _on_tab_double_clicked(self, tab_index):
        """Handle double-click on a tab to trigger rename."""
        self.tab_widget.setCurrentIndex(tab_index)
        
        # Get the current scenario page
        page = self.tab_widget.widget(tab_index)
        if not page:
            return
        
        old_name = page.get_scenario_name()
        
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
            page.set_scenario_name(new_name)
            
            # Update tab text
            self.tab_widget.setTabText(tab_index, new_name)
            
            # Update dictionary
            self.scenario_tabs[new_name] = self.scenario_tabs.pop(old_name)
            self.update_ui_state()
            break
    
    def generate_unique_name(self, base_name):
        """Generate a unique scenario name based on the given base name."""
        if base_name not in self.scenario_tabs:
            return base_name
            
        counter = 1
        while f"{base_name} ({counter})" in self.scenario_tabs:
            counter += 1
            
        return f"{base_name} ({counter})"
    
    def get_current_scenario_page(self):
        """Get the current scenario page and its index."""
        index = self.tab_widget.currentIndex()
        if index < 0:
            return None, -1
        return self.tab_widget.widget(index), index
    
    def new_scenario(self):
        """Create a new STIR scenario."""
        # Generate unique name
        base_name = "New Scenario"
        unique_name = self.generate_unique_name(base_name)
        
        # Create new tab
        new_scenario = STIRScenarioTabPage(self, unique_name)
        new_scenario.scenario_changed.connect(self.on_scenario_changed)
        
        # Set current UOM settings for the new scenario
        new_scenario.set_display_uom(self.depth_uom, self.speed_uom)
        
        tab_index = self.tab_widget.addTab(new_scenario, unique_name)
        self.scenario_tabs[unique_name] = new_scenario
        
        # Switch to the new tab
        self.tab_widget.setCurrentIndex(tab_index)
        self.update_ui_state()
    
    def clone_current_scenario(self):
        """Clone the current STIR scenario."""
        page, _ = self.get_current_scenario_page()
        if not page:
            return
        
        # Generate unique name for clone
        base_name = f"{page.get_scenario_name()} Copy"
        unique_name = self.generate_unique_name(base_name)
        
        # Create clone
        clone_scenario = STIRScenarioTabPage(self, unique_name)
        clone_scenario.scenario_changed.connect(self.on_scenario_changed)
        
        # Set UOM settings for the clone
        clone_scenario.set_display_uom(self.depth_uom, self.speed_uom)
        
        # Copy operations data
        operations_data = page.get_operations_data()
        clone_scenario.set_operations_data(operations_data)
        
        # Add to tab widget
        tab_index = self.tab_widget.addTab(clone_scenario, unique_name)
        self.scenario_tabs[unique_name] = clone_scenario
        
        # Switch to the clone tab
        self.tab_widget.setCurrentIndex(tab_index)
        self.update_ui_state()
    
    def delete_current_scenario(self):
        """Delete the current scenario tab with confirmation."""
        page, index = self.get_current_scenario_page()
        if index < 0:
            return
        
        scenario_name = page.get_scenario_name()
        
        # Confirm deletion
        result = QMessageBox.question(
            self, "Confirm Deletion",
            f"Are you sure you want to remove this scenario?\n\n'{scenario_name}'",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Handle deletion
            if self.tab_widget.count() <= 1:
                # Last tab - remove it and create a new blank one
                self.tab_widget.removeTab(index)
                del self.scenario_tabs[scenario_name]
                
                # Create a new blank scenario
                self.new_scenario()
            else:
                # Normal deletion - just remove the tab
                self.tab_widget.removeTab(index)
                del self.scenario_tabs[scenario_name]
                
            self.update_ui_state()
    
    def compare_scenarios(self):
        """Compare STIR scenarios."""
        # This would navigate to a STIR comparison page
        QMessageBox.information(
            self, "Compare Scenarios", 
            "STIR scenarios comparison page - coming soon!"
        )
    
    def export_scenarios(self):
        """Export STIR scenarios."""
        # This would export scenarios to Excel
        QMessageBox.information(
            self, "Export Scenarios", 
            "STIR scenarios export functionality - coming soon!"
        )
    
    def on_scenario_changed(self, scenario_page):
        """Handle changes to a scenario."""
        self.update_ui_state()
    
    def on_tab_changed(self, index):
        """Handle tab change events."""
        self.update_ui_state()
    
    def _on_tab_moved(self, index):
        """Handle tab reordering to keep internal data structures in sync."""
        # Rebuild the scenario_tabs dictionary to match the new tab order
        new_scenario_tabs = {}
        
        for i in range(self.tab_widget.count()):
            tab_page = self.tab_widget.widget(i)
            scenario_name = tab_page.get_scenario_name()
            new_scenario_tabs[scenario_name] = tab_page
        
        # Update our data structure
        self.scenario_tabs = new_scenario_tabs
    
    def update_ui_state(self):
        """Update UI state based on current tabs."""
        has_tabs = self.tab_widget.count() > 0
        
        # Enable/disable buttons based on tab availability
        self.action_buttons["Clone Current"].setEnabled(has_tabs)
        self.action_buttons["Delete"].setEnabled(has_tabs)
        self.action_buttons["Compare Scenarios"].setEnabled(has_tabs and self.tab_widget.count() > 1)
        self.action_buttons["Export"].setEnabled(has_tabs)
        
        # Update scenario info display
        page, _ = self.get_current_scenario_page()
        if not page:
            scenario_name = "No scenario selected"
            total_stir = 0
            operations_count = 0
        else:
            scenario_name = page.get_scenario_name()
            total_stir = page.get_total_stir()
            operations_count = page.get_operations_count()
                    
        # Update combined title
        self.scenario_info_title.setText(
            f"{scenario_name}: {operations_count} operations | "
            f"Total STIR: {total_stir}"
        )
        
        # Update scorebar
        if total_stir > 0:
            if total_stir < 200:
                intensity = "Light"
            elif total_stir < 400:
                intensity = "Medium"
            elif total_stir < 600:
                intensity = "Intense"
            else:
                intensity = "Very Intense"
            
            self.stir_score_bar.set_value(total_stir, intensity)
        else:
            self.stir_score_bar.set_value(0, "No operations")
    
    def open_custom_machine_manager(self):
        """Open the custom machine management dialog."""
        from .delegates.custom_machine_manager_dialog import CustomMachineManagerDialog
        
        dialog = CustomMachineManagerDialog(self)
        dialog.exec()