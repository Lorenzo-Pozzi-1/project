"""Season Planner page for the LORENZO POZZI Pesticide App."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from common.styles import MARGIN_LARGE, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE, get_title_font
from common.widgets import HeaderWithBackButton, ContentFrame, ScoreBar
from season_planner_page.widgets import SeasonPlanMetadataWidget, ApplicationsTableContainer


class SeasonPlannerPage(QWidget):
    """Season Planner page for managing seasonal pesticide application plans."""
    
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
        header = HeaderWithBackButton("Season Planner")
        header.back_clicked.connect(self.parent.go_home)
        
        # Add Compare button to the header
        compare_button = QPushButton("Compare Plans")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.setMaximumWidth(150)
        compare_button.clicked.connect(self.compare_plans)
        header.layout().addWidget(compare_button)
        
        main_layout.addWidget(header)
        
        # Season Plan Metadata Widget
        self.metadata_widget = SeasonPlanMetadataWidget()
        self.metadata_widget.metadata_changed.connect(self.on_metadata_changed)
        main_layout.addWidget(self.metadata_widget)
        
        # Applications Table Frame
        applications_frame = ContentFrame()
        applications_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Applications")
        title_label.setFont(get_title_font(size=16))
        applications_layout.addWidget(title_label)
        
        # Applications Table Container
        self.applications_container = ApplicationsTableContainer()
        self.applications_container.applications_changed.connect(self.update_eiq_display)
        applications_layout.addWidget(self.applications_container)
        
        # Button to add new application
        buttons_layout = QHBoxLayout()
        add_button = QPushButton("Add Application")
        add_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_button.clicked.connect(self.add_application)
        buttons_layout.addWidget(add_button)
        buttons_layout.addStretch(1)
        
        applications_layout.addLayout(buttons_layout)
        applications_frame.layout.addLayout(applications_layout)
        main_layout.addWidget(applications_frame)
        
        # EIQ Results Display with Score Bar
        results_frame = ContentFrame()
        results_layout = QVBoxLayout()
        
        # Title
        results_title = QLabel("Season EIQ Impact")
        results_title.setFont(get_title_font(size=16))
        results_layout.addWidget(results_title)
        
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
        eiq_info_layout.addWidget(QLabel("Total Field EIQ:"))
        self.total_eiq_value = QLabel("0")
        eiq_info_layout.addWidget(self.total_eiq_value)
        
        eiq_info_layout.addSpacing(20)
        
        eiq_info_layout.addWidget(QLabel("Applications Count:"))
        self.applications_count_value = QLabel("0")
        eiq_info_layout.addWidget(self.applications_count_value)
        
        eiq_info_layout.addStretch(1)
        results_layout.addLayout(eiq_info_layout)
        
        results_frame.layout.addLayout(results_layout)
        main_layout.addWidget(results_frame)
    
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
        total_eiq = self.applications_container.get_total_field_eiq()
        applications = self.applications_container.get_applications()
        
        # Update score bar
        self.eiq_score_bar.set_value(total_eiq if total_eiq > 0 else 0, 
                                     "" if total_eiq > 0 else "No applications")
        
        # Update labels
        self.total_eiq_value.setText(f"{total_eiq:.2f}")
        self.applications_count_value.setText(str(len(applications)))
    
    def compare_plans(self):
        """Placeholder function for comparing multiple plans."""
        print("Compare Plans clicked")
    
    def refresh_product_data(self):
        """Refresh product data when filtered products change in the main window."""
        applications = self.applications_container.get_applications()
        self.applications_container.set_applications(applications)