"""
Season Planner page for the LORENZO POZZI Pesticide App.

This module defines the SeasonPlannerPage class which provides functionality
for planning and managing seasonal pesticide applications.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtCore import Qt
from common.styles import (MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, 
                         SECONDARY_BUTTON_STYLE, get_title_font, get_body_font)
from common.widgets import HeaderWithBackButton, ContentFrame, ScoreBar
from season_planner.plan_metadata_widget import SeasonPlanMetadataWidget
from season_planner.applications_table_widget import ApplicationsTableWidget
from eiq_calculator.eiq_calculations import format_eiq_result


class SeasonPlannerPage(QWidget):
    """
    Season Planner page for managing seasonal application plans.
    
    This page allows users to create, edit, and compare seasonal pesticide
    application plans to optimize EIQ impact across multiple fields.
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
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button and compare button
        header_layout = QHBoxLayout()
        
        # Header with back button
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        
        # Add Compare button directly to the header (right side)
        compare_button = QPushButton("Compare Plans")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.setMaximumWidth(150)
        # Placeholder for compare functionality
        compare_button.clicked.connect(self.compare_plans)
        
        # Add the Compare button to the header's layout (right side)
        header.layout().addWidget(compare_button)
        
        # Add the header to the main layout
        main_layout.addWidget(header)
        
        # Season Plan Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        self.metadata_widget.metadata_changed.connect(self.on_metadata_changed)
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        
        # Table Header
        table_header = QLabel("Applications")
        table_header.setFont(get_title_font(size=16))
        applications_layout.addWidget(table_header)
        
        # Applications Table
        self.applications_table = ApplicationsTableWidget()
        self.applications_table.applications_changed.connect(self.update_eiq_display)
        applications_layout.addWidget(self.applications_table)
        
        # Buttons for table actions
        buttons_layout = QHBoxLayout()
        
        add_application_button = QPushButton("Add Application")
        add_application_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_application_button.clicked.connect(self.add_application)
        buttons_layout.addWidget(add_application_button)
        
        remove_application_button = QPushButton("Remove Selected")
        remove_application_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        remove_application_button.clicked.connect(self.remove_application)
        buttons_layout.addWidget(remove_application_button)
        
        # Add spacer to push buttons to the left
        buttons_layout.addStretch(1)
        
        applications_layout.addLayout(buttons_layout)
        applications_frame.layout.addLayout(applications_layout)
        main_layout.addWidget(applications_frame)
        
        # EIQ Results Display with Score Bar
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        results_title = QLabel("Season EIQ Impact")
        results_title.setFont(get_title_font(size=16))
        results_layout.addWidget(results_title)
        
        # Score bar for EIQ visualization
        self.eiq_score_bar = ScoreBar()
        # Set initial value to 0 (will be updated later with actual calculations)
        self.eiq_score_bar.set_value(0, "No applications")
        results_layout.addWidget(self.eiq_score_bar)
        
        # Add some additional information labels
        eiq_info_layout = QHBoxLayout()
        
        applications_count_label = QLabel("Applications Count:")
        applications_count_label.setFont(get_body_font())
        eiq_info_layout.addWidget(applications_count_label)
        
        self.applications_count_value = QLabel("0")
        self.applications_count_value.setFont(get_body_font())
        eiq_info_layout.addWidget(self.applications_count_value)

        eiq_info_layout.addStretch(1)
        
        results_layout.addLayout(eiq_info_layout)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
    def on_metadata_changed(self):
        """Handle changes to season plan metadata."""
        # Update field area in applications table
        metadata = self.metadata_widget.get_metadata()
        self.applications_table.set_field_area(
            metadata["field_area"], 
            metadata["field_area_uom"]
        )
    
    def add_application(self):
        """Add a new application row to the table."""
        self.applications_table.add_application_row()
    
    def remove_application(self):
        """Remove the selected application row from the table."""
        self.applications_table.remove_application_row()
    
    def update_eiq_display(self):
        """Update the EIQ display based on current applications."""
        # Get total field EIQ
        total_eiq = self.applications_table.get_total_field_eiq()
        
        # Get applications count
        applications = self.applications_table.get_applications()
        application_count = len(applications)
        
        # Update score bar
        if total_eiq > 0:
            self.eiq_score_bar.set_value(total_eiq)
        else:
            self.eiq_score_bar.set_value(0, "No applications")
        
        # Update labels
        ha_text, acre_text = format_eiq_result(total_eiq)
        self.total_eiq_value.setText(ha_text)
        self.applications_count_value.setText(str(application_count))
    
    def compare_plans(self):
        """Placeholder function for comparing multiple plans."""
        # This will be implemented later
        print("Compare Plans clicked")
    
    def refresh_product_data(self):
        """
        Refresh product data based on the filtered products.
        
        This method is called when filtered data changes in the main window.
        """
        # Since the applications table loads products dynamically, 
        # we need to rebuild any existing rows with the new product list
        applications = self.applications_table.get_applications()
        self.applications_table.set_applications(applications)