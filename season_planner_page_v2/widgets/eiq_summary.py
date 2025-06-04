"""
EIQ Summary Widget for Season Planner V2.

Widget for displaying EIQ calculation results and environmental impact scoring.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Signal

from common import ContentFrame, ScoreBar, get_subtitle_font


class EIQSummaryWidget(QWidget):
    """
    Widget for displaying EIQ summary information and environmental impact scoring.
    
    Shows total Field EIQ, application count, and regenerative agriculture
    framework classification.
    """
    
    def __init__(self, parent=None):
        """Initialize the EIQ summary widget."""
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create content frame
        content_frame = ContentFrame()
        content_layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Scenario EIQ Impact")
        title_label.setFont(get_subtitle_font())
        content_layout.addWidget(title_label)
        
        # Create score bar with regenerative agriculture thresholds
        self.eiq_score_bar = ScoreBar(
            thresholds=[200, 500, 800, 2500],
            labels=["Leading", "Advanced", "Engaged", "Onboarding", "Out of range"],
            min_value=0,
            max_value=2500,
            title_text="RegenAg framework class:"
        )
        self.eiq_score_bar.set_value(0, "No applications")
        content_layout.addWidget(self.eiq_score_bar)
        
        # Information layout
        info_layout = QHBoxLayout()
        
        # Total EIQ
        info_layout.addWidget(QLabel("Total Field EIQ:"))
        self.total_eiq_label = QLabel("0.00")
        info_layout.addWidget(self.total_eiq_label)
        
        info_layout.addSpacing(20)
        
        # Application count
        info_layout.addWidget(QLabel("Applications Count:"))
        self.app_count_label = QLabel("0")
        info_layout.addWidget(self.app_count_label)
        
        info_layout.addStretch()
        content_layout.addLayout(info_layout)
        
        content_frame.layout.addLayout(content_layout)
        main_layout.addWidget(content_frame)
    
    def update_eiq_data(self, total_eiq, application_count):
        """
        Update the EIQ display with new data.
        
        Args:
            total_eiq (float): Total Field EIQ value
            application_count (int): Number of applications
        """
        # Update score bar
        self.eiq_score_bar.set_value(
            total_eiq if total_eiq > 0 else 0,
            "" if total_eiq > 0 else "No applications"
        )
        
        # Update text labels
        self.total_eiq_label.setText(f"{total_eiq:.2f}")
        self.app_count_label.setText(str(application_count))
    
    def clear(self):
        """Clear the EIQ display."""
        self.update_eiq_data(0.0, 0)
    
    def get_current_eiq(self):
        """Get the current EIQ value."""
        try:
            return float(self.total_eiq_label.text())
        except ValueError:
            return 0.0
    
    def get_current_app_count(self):
        """Get the current application count."""
        try:
            return int(self.app_count_label.text())
        except ValueError:
            return 0