"""
Previous Season page for the LORENZO POZZI Pesticide App.

This module defines the PreviousSeasonPage class for creating a new season
based on a previous year's plan, allowing users to load and modify existing seasons.
"""

import os
import datetime
import shutil
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QStackedWidget, QSplitter, QFrame
)
from PySide6.QtCore import Qt, Signal

from ui.common.styles import (
    MARGIN_LARGE, SPACING_MEDIUM, SPACING_LARGE, PRIMARY_BUTTON_STYLE, 
    SECONDARY_BUTTON_STYLE, get_subtitle_font, get_body_font
)
from ui.common.widgets import ContentFrame

from ui.season_planner.models import Season, Application, SeasonStorage
from ui.season_planner.utils_and_components import (
    ApplicationEditor, SeasonSummary, ApplicationListWidget
)


class PreviousSeasonPage(QWidget):
    """
    Page for creating a new season plan based on a previous year's plan.
    
    This page allows users to select and load a previous season, modify it,
    and save it as a new season.
    """
    
    def __init__(self, parent=None):
        """Initialize the previous season page."""
        super().__init__(parent)
        self.parent = parent
        
        # Current loaded season
        self.loaded_season = None
        self.loaded_file_path = None
        
        # Season after modifications (for saving as new)
        self.modified_season = None
        
        # Track whether we're editing an application
        self.current_app_index = -1
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()
        
        # Selection view (index 0)
        self.init_selection_view()
        
        # Season editing view (index 1)
        self.init_editing_view()
        
        main_layout.addWidget(self.stacked_widget)
        
        # Bottom buttons (always visible)
        buttons_layout = QHBoxLayout()
        
        back_button = QPushButton("< Back to Season Options")
        back_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        back_button.clicked.connect(self.parent.go_back_to_main)
        
        self.save_button = QPushButton("Save as New Season")
        self.save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_as_new_season)
        self.save_button.setEnabled(False)  # Disabled until a season is loaded
        
        buttons_layout.addWidget(back_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Show the selection view initially
        self.stacked_widget.setCurrentIndex(0)
    
    def init_selection_view(self):
        """Initialize the view for selecting a previous season."""
        selection_widget = QWidget()
        selection_layout = QVBoxLayout(selection_widget)
        selection_layout.setContentsMargins(0, 0, 0, 0)
        
        # Instructions frame
        instructions_frame = ContentFrame()
        instructions_layout = QVBoxLayout()
        
        instructions_title = QLabel("Select a Previous Season")
        instructions_title.setFont(get_subtitle_font(size=16))
        
        instructions_text = QLabel(
            "Select a season from the list below, or browse to locate a season file. "
            "You can then modify the season and save it as a new season with updated dates."
        )
        instructions_text.setWordWrap(True)
        instructions_text.setFont(get_body_font())
        
        instructions_layout.addWidget(instructions_title)
        instructions_layout.addWidget(instructions_text)
        
        instructions_frame.layout.addLayout(instructions_layout)
        selection_layout.addWidget(instructions_frame)
        
        # Previous seasons list
        seasons_frame = ContentFrame()
        seasons_layout = QVBoxLayout()
        
        seasons_title = QLabel("Recent Seasons")
        seasons_title.setFont(get_subtitle_font(size=14))
        seasons_layout.addWidget(seasons_title)
        
        self.seasons_list = QListWidget()
        self.seasons_list.setMinimumHeight(200)
        self.seasons_list.itemDoubleClicked.connect(self.load_selected_season)
        seasons_layout.addWidget(self.seasons_list)
        
        # Browse button
        browse_button = QPushButton("Browse for Season File...")
        browse_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        browse_button.clicked.connect(self.browse_for_season)
        seasons_layout.addWidget(browse_button, alignment=Qt.AlignRight)
        
        seasons_frame.layout.addLayout(seasons_layout)
        selection_layout.addWidget(seasons_frame)
        
        self.stacked_widget.addWidget(selection_widget)
    
    def init_editing_view(self):
        """Initialize the view for editing a loaded season."""
        editing_widget = QWidget()
        editing_layout = QVBoxLayout(editing_widget)
        editing_layout.setContentsMargins(0, 0, 0, 0)
        editing_layout.setSpacing(SPACING_MEDIUM)
        
        # Season details header
        self.season_title = QLabel("Season Details")
        self.season_title.setFont(get_subtitle_font(size=18))
        editing_layout.addWidget(self.season_title)
        
        # Season info frame
        season_info_frame = ContentFrame()
        season_info_layout = QHBoxLayout()
        
        # Original season info
        original_info_layout = QVBoxLayout()
        original_label = QLabel("Original Season")
        original_label.setFont(get_subtitle_font(size=14))
        original_info_layout.addWidget(original_label)
        
        self.original_info = QLabel()
        self.original_info.setWordWrap(True)
        self.original_info.setFont(get_body_font())
        original_info_layout.addWidget(self.original_info)
        
        season_info_layout.addLayout(original_info_layout)
        
        # Add divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setFrameShadow(QFrame.Sunken)
        season_info_layout.addWidget(divider)
        
        # New season options
        new_season_layout = QVBoxLayout()
        new_season_label = QLabel("New Season")
        new_season_label.setFont(get_subtitle_font(size=14))
        new_season_layout.addWidget(new_season_label)
        
        self.new_season_info = QLabel()
        self.new_season_info.setWordWrap(True)
        self.new_season_info.setFont(get_body_font())
        new_season_layout.addWidget(self.new_season_info)
        
        # Buttons for modifying the new season
        buttons_layout = QHBoxLayout()
        
        update_year_button = QPushButton("Update Year")
        update_year_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        update_year_button.clicked.connect(self.update_season_year)
        
        update_dates_button = QPushButton("Adjust Application Dates")
        update_dates_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        update_dates_button.clicked.connect(self.adjust_application_dates)
        
        buttons_layout.addWidget(update_year_button)
        buttons_layout.addWidget(update_dates_button)
        
        new_season_layout.addLayout(buttons_layout)
        season_info_layout.addLayout(new_season_layout)
        
        season_info_frame.layout.addLayout(season_info_layout)
        editing_layout.addWidget(season_info_frame)
        
        # Applications section
        self.app_list = ApplicationListWidget()
        self.app_list.application_selected.connect(self.edit_application)
        self.app_list.add_application_requested.connect(self.add_application)
        self.app_list.remove_application_requested.connect(self.remove_application)
        editing_layout.addWidget(self.app_list)
        
        # Season summary
        self.season_summary = SeasonSummary()
        editing_layout.addWidget(self.season_summary)
        
        # Return to selection button
        back_to_selection_button = QPushButton("< Back to Season Selection")
        back_to_selection_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        back_to_selection_button.clicked.connect(self.return_to_selection)
        editing_layout.addWidget(back_to_selection_button, alignment=Qt.AlignLeft)
        
        # Add the editing widget to the stacked widget
        self.stacked_widget.addWidget(editing_widget)
    
    def on_show(self):
        """Called when the page is shown."""
        # Load recent seasons list
        self.load_recent_seasons()
        
        # Reset to selection view
        self.stacked_widget.setCurrentIndex(0)
        
        # Reset loaded season
        self.loaded_season = None
        self.loaded_file_path = None
        self.modified_season = None
        self.save_button.setEnabled(False)
    
    def load_recent_seasons(self):
        """Load and display the list of recent seasons."""
        self.seasons_list.clear()
        
        # Default location for season files
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "seasons")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Get list of season files
        seasons = SeasonStorage.list_saved_seasons(data_dir)
        
        if not seasons:
            # Add placeholder item if no seasons found
            item = QListWidgetItem("No saved seasons found")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # Make non-selectable
            self.seasons_list.addItem(item)
            return
        
        # Add season files to list
        for season in seasons:
            # Format display text
            year_str = f" ({season['year']})" if season['year'] else ""
            grower_str = f" - {season['grower']}" if season['grower'] else ""
            crop_str = f" - {season['crop']}" if season['crop'] else ""
            
            display_text = f"{season['name']}{year_str}{grower_str}{crop_str}"
            
            # Create list item
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, season['file_path'])
            
            self.seasons_list.addItem(item)
    
    def browse_for_season(self):
        """Open a file dialog to browse for a season file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Season File",
            os.path.expanduser("~"),
            "Season Files (*.json)"
        )
        
        if file_path:
            self.load_season_file(file_path)
    
    def load_selected_season(self, item):
        """
        Load the season selected from the list.
        
        Args:
            item: The selected QListWidgetItem
        """
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.load_season_file(file_path)
    
    def load_season_file(self, file_path):
        """
        Load a season from a file.
        
        Args:
            file_path: Path to the season file
        """
        # Load the season
        season = SeasonStorage.load_season(file_path)
        
        if not season:
            QMessageBox.warning(
                self,
                "Load Error",
                "Failed to load the selected season file."
            )
            return
        
        # Store the loaded season and file path
        self.loaded_season = season
        self.loaded_file_path = file_path
        
        # Create a copy for modifications
        self.modified_season = Season.from_dict(season.to_dict())
        
        # Update the season names to indicate it's a copy
        self.modified_season.name = f"{season.name} - Copy"
        
        # Update UI with loaded season
        self.update_season_display()
        
        # Switch to editing view
        self.stacked_widget.setCurrentIndex(1)
        
        # Enable save button
        self.save_button.setEnabled(True)
    
    def update_season_display(self):
        """Update the UI with the loaded season data."""
        if not self.loaded_season or not self.modified_season:
            return
        
        # Update title
        self.season_title.setText(f"Season: {self.modified_season.name}")
        
        # Update original season info
        original_info = (
            f"<b>Season:</b> {self.loaded_season.name}<br>"
            f"<b>Year:</b> {self.loaded_season.year}<br>"
            f"<b>Grower:</b> {self.loaded_season.grower or 'Not specified'}<br>"
            f"<b>Farm:</b> {self.loaded_season.farm or 'Not specified'}<br>"
            f"<b>Crop:</b> {self.loaded_season.crop or 'Not specified'}<br>"
            f"<b>Variety:</b> {self.loaded_season.variety or 'Not specified'}<br>"
            f"<b>Applications:</b> {len(self.loaded_season.applications)}"
        )
        self.original_info.setText(original_info)
        
        # Update new season info
        new_info = (
            f"<b>Season:</b> {self.modified_season.name}<br>"
            f"<b>Year:</b> {self.modified_season.year}<br>"
            f"<b>Grower:</b> {self.modified_season.grower or 'Not specified'}<br>"
            f"<b>Farm:</b> {self.modified_season.farm or 'Not specified'}<br>"
            f"<b>Crop:</b> {self.modified_season.crop or 'Not specified'}<br>"
            f"<b>Variety:</b> {self.modified_season.variety or 'Not specified'}<br>"
            f"<b>Applications:</b> {len(self.modified_season.applications)}"
        )
        self.new_season_info.setText(new_info)
        
        # Update applications list
        self.app_list.update_applications(self.modified_season.applications)
        
        # Update summary
        self.season_summary.update_summary(self.modified_season)
    
    def update_season_year(self):
        """Update the year of the modified season to the current year."""
        if not self.modified_season:
            return
        
        # Get current year
        current_year = datetime.date.today().year
        
        # Check if it's already the current year
        if self.modified_season.year == current_year:
            QMessageBox.information(
                self,
                "Already Current",
                f"The season is already set to the current year ({current_year})."
            )
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            self,
            "Update Year",
            f"Update the season year from {self.modified_season.year} to {current_year}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Update season year
            self.modified_season.year = current_year
            
            # Update display
            self.update_season_display()
    
    def adjust_application_dates(self):
        """Adjust application dates based on the year difference."""
        if not self.loaded_season or not self.modified_season:
            return
        
        # Calculate year difference
        year_diff = self.modified_season.year - self.loaded_season.year
        
        # If no difference, ask user if they want to shift dates anyway
        if year_diff == 0:
            reply = QMessageBox.question(
                self,
                "Adjust Dates",
                "There is no year difference. Do you want to adjust dates to the current month?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            # Set year diff to 0 to keep year the same
            year_diff = 0
        else:
            # Confirm date adjustment
            reply = QMessageBox.question(
                self,
                "Adjust Dates",
                f"Adjust all application dates by {year_diff} year(s)?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Update all application dates
        for app in self.modified_season.applications:
            try:
                # Create new date with adjusted year
                new_date = datetime.date(
                    app.date.year + year_diff,
                    app.date.month,
                    min(app.date.day, 28)  # Avoid February 29 issues
                )
                app.date = new_date
            except ValueError:
                # Handle invalid dates (like February 29 in non-leap years)
                app.date = datetime.date(
                    app.date.year + year_diff,
                    app.date.month,
                    28
                )
        
        # Update display
        self.update_season_display()
    
    def edit_application(self, application):
        """
        Open an editor for the selected application.
        
        Args:
            application: The Application to edit
        """
        # Find the application index
        self.current_app_index = -1
        for i, app in enumerate(self.modified_season.applications):
            if app.id == application.id:
                self.current_app_index = i
                break
        
        # Create a dialog to edit the application
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Application")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        dialog_layout = QVBoxLayout(dialog)
        
        # Create an application editor
        app_editor = ApplicationEditor(self, application)
        app_editor.application_updated.connect(lambda app: self.update_application(app, dialog))
        app_editor.cancel_button.clicked.connect(dialog.reject)
        
        dialog_layout.addWidget(app_editor)
        
        # Show the dialog
        dialog.exec()
    
    def update_application(self, application, dialog):
        """
        Update an application and close the editor dialog.
        
        Args:
            application: The updated Application
            dialog: The dialog to close
        """
        if self.current_app_index >= 0:
            # Update existing application
            self.modified_season.applications[self.current_app_index] = application
            
            # Update display
            self.update_season_display()
            
            # Close the dialog
            dialog.accept()
    
    def add_application(self):
        """Add a new application to the season."""
        if not self.modified_season:
            return
        
        # Create a dialog to add the application
        from PySide6.QtWidgets import QDialog, QVBoxLayout
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Application")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        dialog_layout = QVBoxLayout(dialog)
        
        # Create an empty application
        application = Application()
        
        # Create an application editor
        app_editor = ApplicationEditor(self, application)
        app_editor.application_updated.connect(lambda app: self.add_new_application(app, dialog))
        app_editor.cancel_button.clicked.connect(dialog.reject)
        
        dialog_layout.addWidget(app_editor)
        
        # Show the dialog
        dialog.exec()
    
    def add_new_application(self, application, dialog):
        """
        Add a new application to the season and close the dialog.
        
        Args:
            application: The new Application
            dialog: The dialog to close
        """
        if self.modified_season:
            # Add the application
            self.modified_season.add_application(application)
            
            # Update display
            self.update_season_display()
            
            # Close the dialog
            dialog.accept()
    
    def remove_application(self, index):
        """
        Remove an application from the season.
        
        Args:
            index: Index of the application to remove
        """
        if not self.modified_season or index < 0 or index >= len(self.modified_season.applications):
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            "Are you sure you want to delete this application?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the application
            self.modified_season.remove_application(index)
            
            # Update display
            self.update_season_display()
    
    def return_to_selection(self):
        """Return to the season selection view."""
        # Confirm if there are unsaved changes
        if self.modified_season:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Are you sure you want to go back to selection?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
        
        # Clear loaded season
        self.loaded_season = None
        self.loaded_file_path = None
        self.modified_season = None
        
        # Disable save button
        self.save_button.setEnabled(False)
        
        # Switch to selection view
        self.stacked_widget.setCurrentIndex(0)
        
        # Reload recent seasons
        self.load_recent_seasons()
    
    def save_as_new_season(self):
        """Save the modified season as a new season."""
        if not self.modified_season:
            return
        
        # Choose save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Season As",
            os.path.expanduser("~"),
            "Season Files (*.json)"
        )
        
        if not file_path:
            return
        
        # Ensure file has .json extension
        if not file_path.endswith('.json'):
            file_path += '.json'
        
        # Save the season
        if SeasonStorage.save_season(self.modified_season, file_path):
            QMessageBox.information(
                self,
                "Season Saved",
                f"Season '{self.modified_season.name}' has been saved successfully."
            )
            
            # Return to selection view
            self.return_to_selection()
        else:
            QMessageBox.warning(
                self,
                "Save Error",
                "An error occurred while saving the season."
            )