"""Season Planner page for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton)
from common.styles import (MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, 
                         SECONDARY_BUTTON_STYLE, get_title_font, get_body_font)
from common.widgets import HeaderWithBackButton, ContentFrame, ScoreBar
from season_planner_page.widgets import SeasonPlanMetadataWidget, ApplicationsTableContainer


class SeasonPlannerPage(QWidget):
    """Season Planner page for managing seasonal pesticide application plans."""
    
    def __init__(self, parent=None):
        """Initialize the season planner page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def _create_label(self, text, layout, title=False, size=None):
        """Create a label with specified styling and add it to layout."""
        label = QLabel(text)
        font_func = get_title_font if title else get_body_font
        if size is not None:  # Only pass size parameter if it's not None
            label.setFont(font_func(size=size))
        else:
            label.setFont(font_func())  # Use default size
        layout.addWidget(label)
        return label
    
    def _create_button(self, text, style, callback, layout=None, max_width=None):
        """Create a button with specified styling and callback."""
        button = QPushButton(text)
        button.setStyleSheet(style)
        if max_width:
            button.setMaximumWidth(max_width)
        button.clicked.connect(callback)
        if layout:
            layout.addWidget(button)
        return button
    
    def _create_content_frame(self, title, main_layout):
        """Create a content frame with a title."""
        frame = ContentFrame()
        layout = QVBoxLayout()
        
        # Add title
        self._create_label(title, layout, title=True, size=16)
            
        frame.layout.addLayout(layout)
        main_layout.addWidget(frame)
        return frame, layout
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Header with back button and compare button
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        
        # Add Compare button to the header (right side)
        self._create_button("Compare Plans", PRIMARY_BUTTON_STYLE, 
                           self.compare_plans, max_width=150, 
                           layout=header.layout())
        
        main_layout.addWidget(header)
        
        # Season Plan Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        self.metadata_widget.metadata_changed.connect(self.on_metadata_changed)
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame, applications_layout = self._create_content_frame("Applications", main_layout)
        
        # Applications Table Container
        self.applications_container = ApplicationsTableContainer()
        self.applications_container.applications_changed.connect(self.update_eiq_display)
        applications_layout.addWidget(self.applications_container)
        
        # Button to add new application
        buttons_layout = QHBoxLayout()
        self._create_button("Add Application", PRIMARY_BUTTON_STYLE, 
                           self.add_application, buttons_layout)
        buttons_layout.addStretch(1)  # Add spacer to push buttons to the left
        
        applications_layout.addLayout(buttons_layout)
        
        # EIQ Results Display with Score Bar
        results_frame, results_layout = self._create_content_frame("Season EIQ Impact", main_layout)
        
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
        self._create_label("Total Field EIQ:", eiq_info_layout)
        self.total_eiq_value = self._create_label("0", eiq_info_layout)
        
        eiq_info_layout.addSpacing(20)
        
        self._create_label("Applications Count:", eiq_info_layout)
        self.applications_count_value = self._create_label("0", eiq_info_layout)
        
        eiq_info_layout.addStretch(1)
        results_layout.addLayout(eiq_info_layout)
    
    def on_metadata_changed(self):
        """Handle changes to season plan metadata."""
        metadata = self.metadata_widget.get_metadata()
        self.applications_container.set_field_area(
            metadata["field_area"], 
            metadata["field_area_uom"]
        )
    
    def add_application(self):
        """Add a new application row to the container."""
        self.applications_container.add_application_row()
    
    def update_eiq_display(self):
        """Update the EIQ display based on current applications."""
        # Get total field EIQ and application count
        total_eiq = self.applications_container.get_total_field_eiq()
        applications = self.applications_container.get_applications()
        application_count = len(applications)
        
        # Update score bar
        if total_eiq > 0:
            self.eiq_score_bar.set_value(total_eiq)
        else:
            self.eiq_score_bar.set_value(0, "No applications")
        
        # Update labels
        self.total_eiq_value.setText(f"{total_eiq:.2f}")
        self.applications_count_value.setText(str(application_count))
    
    def compare_plans(self):
        """Placeholder function for comparing multiple plans."""
        print("Compare Plans clicked")
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        applications = self.applications_container.get_applications()
        self.applications_container.set_applications(applications)