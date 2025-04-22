"""
New Season page for the LORENZO POZZI Pesticide App.

This module defines the NewSeasonPage class for creating a new season from scratch,
allowing users to set up season information and add applications.
"""

import os
import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QSpinBox, QTabWidget, QMessageBox, QFileDialog, QComboBox
)
from PySide6.QtCore import Qt, Signal

from ui.common.styles import (
    MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
)
from ui.common.widgets import ContentFrame

from ui.season_planner.models import Season, Application, SeasonStorage
from ui.season_planner.utils_and_components import (
    ApplicationEditor, SeasonSummary, ApplicationListWidget
)


class NewSeasonPage(QWidget):
    """
    Page for creating a new season plan from scratch.
    
    This page allows users to set up a new growing season and add applications.
    """
    
    def __init__(self, parent=None):
        """Initialize the new season page."""
        super().__init__(parent)
        self.parent = parent
        
        # Create a new empty season
        self.season = Season()
        
        # Track whether we're editing an application
        self.current_app_index = -1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Season details
        self.init_season_details()
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        
        # Summary tab
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        
        # Season summary widget
        self.season_summary = SeasonSummary()
        summary_layout.addWidget(self.season_summary)
        
        # Applications list
        self.app_list = ApplicationListWidget()
        self.app_list.application_selected.connect(self.edit_application)
        self.app_list.add_application_requested.connect(self.add_application)
        self.app_list.remove_application_requested.connect(self.remove_application)
        summary_layout.addWidget(self.app_list)
        
        self.tabs.addTab(self.summary_tab, "Summary")
        
        # Application editor tab
        self.app_editor_tab = QWidget()
        app_editor_layout = QVBoxLayout(self.app_editor_tab)
        
        # Application editor
        self.app_editor = ApplicationEditor()
        self.app_editor.application_updated.connect(self.application_saved)
        app_editor_layout.addWidget(self.app_editor)
        
        self.tabs.addTab(self.app_editor_tab, "Edit Application")
        
        # Start with summary tab
        self.tabs.setCurrentIndex(0)
        
        main_layout.addWidget(self.tabs)
        
        # Bottom buttons
        buttons_layout = QHBoxLayout()
        
        back_button = QPushButton("< Back to Season Options")
        back_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        back_button.clicked.connect(self.parent.go_back_to_main)
        
        save_button = QPushButton("Save Season")
        save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        save_button.clicked.connect(self.save_season)
        
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        
        main_layout.addLayout(buttons_layout)
    
    def init_season_details(self):
        """Initialize the season details section."""
        # Season details frame
        details_frame = ContentFrame()
        details_layout = QFormLayout()
        
        # Season name
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter a name for this season")
        self.name_input.textChanged.connect(self.update_season_name)
        details_layout.addRow("Season Name:", self.name_input)
        
        # Year
        year_layout = QHBoxLayout()
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2000, 2100)
        self.year_spin.setValue(datetime.date.today().year)
        self.year_spin.valueChanged.connect(self.update_season_year)
        year_layout.addWidget(self.year_spin)
        
        # Make field to fill remaining space
        year_layout.addStretch()
        
        details_layout.addRow("Year:", year_layout)
        
        # Grower info
        self.grower_input = QLineEdit()
        self.grower_input.setPlaceholderText("Enter grower name")
        self.grower_input.textChanged.connect(self.update_season_grower)
        details_layout.addRow("Grower:", self.grower_input)
        
        # Farm
        self.farm_input = QLineEdit()
        self.farm_input.setPlaceholderText("Enter farm name or location")
        self.farm_input.textChanged.connect(self.update_season_farm)
        details_layout.addRow("Farm:", self.farm_input)
        
        # Crop
        crop_layout = QHBoxLayout()
        self.crop_combo = QComboBox()
        self.crop_combo.setEditable(True)
        self.crop_combo.addItems(["Potato", "Wheat", "Corn", "Soybean", "Other"])
        self.crop_combo.setCurrentText("")
        self.crop_combo.setPlaceholderText("Select or enter crop")
        self.crop_combo.currentTextChanged.connect(self.update_season_crop)
        crop_layout.addWidget(self.crop_combo)
        
        # Variety
        self.variety_input = QLineEdit()
        self.variety_input.setPlaceholderText("Enter crop variety (if applicable)")
        self.variety_input.textChanged.connect(self.update_season_variety)
        crop_layout.addWidget(self.variety_input)
        
        details_layout.addRow("Crop & Variety:", crop_layout)
        
        details_frame.layout.addLayout(details_layout)
        
        self.layout().addWidget(details_frame)
    
    def on_show(self):
        """Called when the page is shown."""
        # Reset to summary tab
        self.tabs.setCurrentIndex(0)
        
        # Update summary data
        self.update_summary()
    
    def update_season_name(self, name):
        """Update the season name."""
        self.season.name = name
    
    def update_season_year(self, year):
        """Update the season year."""
        self.season.year = year
    
    def update_season_grower(self, grower):
        """Update the season grower."""
        self.season.grower = grower
    
    def update_season_farm(self, farm):
        """Update the season farm."""
        self.season.farm = farm
    
    def update_season_crop(self, crop):
        """Update the season crop."""
        self.season.crop = crop
    
    def update_season_variety(self, variety):
        """Update the season variety."""
        self.season.variety = variety
    
    def update_summary(self):
        """Update the summary and applications list."""
        self.season_summary.update_summary(self.season)
        self.app_list.update_applications(self.season.applications)
    
    def add_application(self):
        """Start adding a new application."""
        # Create a new empty application
        self.current_app_index = -1
        self.app_editor = ApplicationEditor(self)
        self.app_editor.application_updated.connect(self.application_saved)
        
        # Replace the editor tab content
        self.app_editor_tab.layout().takeAt(0)
        if hasattr(self, 'app_editor') and self.app_editor:
            self.app_editor.setParent(None)
        self.app_editor_tab.layout().addWidget(self.app_editor)
        
        # Switch to editor tab
        self.tabs.setCurrentIndex(1)
    
    def edit_application(self, application):
        """
        Edit an existing application.
        
        Args:
            application: The Application to edit
        """
        # Find the application index
        self.current_app_index = -1
        for i, app in enumerate(self.season.applications):
            if app.id == application.id:
                self.current_app_index = i
                break
        
        # Create editor with the application
        self.app_editor = ApplicationEditor(self, application)
        self.app_editor.application_updated.connect(self.application_saved)
        
        # Replace the editor tab content
        self.app_editor_tab.layout().takeAt(0)
        if hasattr(self, 'app_editor') and self.app_editor:
            self.app_editor.setParent(None)
        self.app_editor_tab.layout().addWidget(self.app_editor)
        
        # Switch to editor tab
        self.tabs.setCurrentIndex(1)
    
    def application_saved(self, application):
        """
        Handle saved application from editor.
        
        Args:
            application: The updated Application
        """
        if self.current_app_index >= 0:
            # Update existing application
            self.season.applications[self.current_app_index] = application
        else:
            # Add new application
            self.season.add_application(application)
        
        # Update summary
        self.update_summary()
        
        # Switch back to summary tab
        self.tabs.setCurrentIndex(0)
    
    def cancel_application_edit(self):
        """Cancel application editing."""
        # Switch back to summary tab
        self.tabs.setCurrentIndex(0)
    
    def remove_application(self, index):
        """
        Remove an application.
        
        Args:
            index: Index of the application to remove
        """
        if 0 <= index < len(self.season.applications):
            # Confirm deletion
            reply = QMessageBox.question(
                self, 
                "Confirm Deletion",
                "Are you sure you want to delete this application?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.season.remove_application(index)
                self.update_summary()
    
    def save_season(self):
        """Save the season to a file."""
        # Validate season name
        if not self.season.name:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter a name for the season before saving."
            )
            return
        
        # Choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Season",
            os.path.expanduser("~"),
            "Season Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Ensure file has .json extension
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        # Save the season
        if SeasonStorage.save_season(self.season, file_path):
            QMessageBox.information(
                self,
                "Season Saved",
                f"Season '{self.season.name}' has been saved successfully."
            )
        else:
            QMessageBox.warning(
                self,
                "Save Error",
                "An error occurred while saving the season."
            )