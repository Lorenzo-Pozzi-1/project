"""
Main Season Planner page for the LORENZO POZZI Pesticide App.

This module defines the SeasonPlannerPage class which serves as the container for
the Season Planner functionality, allowing users to start a new season from scratch
or from a previous year's plan.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from common.styles import MARGIN_LARGE, SPACING_LARGE
from common.widgets import HeaderWithBackButton, FeatureButton
from season_planner.new_season_page import NewSeasonPage

class SeasonPlannerPage(QWidget):
    """
    Season Planner page for planning pesticide applications across a growing season.
    
    This page serves as the main container for the Season Planner functionality,
    allowing users to create new seasons or load previous ones.
    """
    
    def __init__(self, parent=None):
        """Initialize the season planner page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Header with back button
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        main_layout.addWidget(header)
        
        # Create stacked widget for different views
        self.stacked_widget = QStackedWidget()

        # Main selection page (index 0)
        self.selection_page = self.create_selection_page()
        self.stacked_widget.addWidget(self.selection_page)
        
        # New season page (index 1)
        self.new_season_page = NewSeasonPage(self)
        self.stacked_widget.addWidget(self.new_season_page)
        
        # Note: The previous season page will be added in the future
        # Previous season page (index 2)
        # self.previous_season_page = PreviousSeasonPage(self)
        # self.stacked_widget.addWidget(self.previous_season_page)
        
        main_layout.addWidget(self.stacked_widget)

        # Show the main selection page initially
        self.stacked_widget.setCurrentIndex(0)
    
    def create_selection_page(self):
        """Create the main selection page with two buttons."""
        selection_page = QWidget()
        selection_layout = QVBoxLayout(selection_page)
        selection_layout.setContentsMargins(0, 0, 0, 0)
        selection_layout.setSpacing(SPACING_LARGE)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        # Create the two main option buttons
        self.start_scratch_button = FeatureButton(
            "Start from scratch",
            "Create a new season plan with no pre-filled data"
        )
        self.start_scratch_button.clicked.connect(self.show_new_season)
        
        self.start_previous_button = FeatureButton(
            "Start from a previous years' plan",
            "Base your new season on an existing plan from your records"
        )
        self.start_previous_button.clicked.connect(self.show_previous_season)
        
        buttons_layout.addWidget(self.start_scratch_button)
        buttons_layout.addWidget(self.start_previous_button)
        
        selection_layout.addLayout(buttons_layout)
        selection_layout.addStretch(1)  # Add stretch to push content to the top
        
        return selection_page

    def show_new_season(self):
        """Switch to the new season page."""
        # Navigate to the new season page (index 1)
        self.stacked_widget.setCurrentIndex(1)
    
    def show_previous_season(self):
        """Switch to the previous season page."""
        print("Previous Season page will be opened")
        # The below code is commented out since the previous_season_page hasn't been developed yet
        # self.stacked_widget.setCurrentIndex(2)
        # Signal to the previous season page that it's being shown
        # self.previous_season_page.on_show()
    
    def go_back_to_main(self):
        """Go back to the main selection page."""
        self.stacked_widget.setCurrentIndex(0)