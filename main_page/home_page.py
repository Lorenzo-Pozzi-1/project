"""
Home page for the LORENZO POZZI Pesticide App

This module defines the HomePage class which serves as the main navigation
screen for the application.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from common.styles import INFO_TEXT_STYLE, MARGIN_LARGE, SPACING_LARGE, TITLE_FONT_SIZE, get_body_font, get_subtitle_font, get_title_font
from common.widgets.widgets import ContentFrame, create_button

class HomePage(QWidget):
    """
    Home page with country selection and feature navigation buttons.
    
    This page serves as the main entry point for users to access the
    various features of the application.
    """
    
    country_changed = Signal(str)
    region_changed = Signal(str)
    
    def __init__(self, parent=None):
        """Initialize the home page."""
        super().__init__(parent)
        self.parent = parent
        self.initializing = True  # Flag to avoid multiple filtering during setup
        self.setup_ui()
        self.initializing = False  # Setup complete
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Header with logo, title, country/region selection in a ContentFrame
        header_frame = ContentFrame()
        header_main_layout = QVBoxLayout()
        
        # Top row with logos and title
        top_layout = QHBoxLayout()
        
        # Logo on the left
        left_logo_label = QLabel()
        pixmap = QPixmap(".\main_page\McCain-Logo.png")
        left_logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(left_logo_label, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Title in the center
        title_label = QLabel("McCain Pesticides App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        top_layout.addWidget(title_label, 1)
        
        # Logo on the right
        right_logo_label = QLabel()
        right_logo_pixmap = QPixmap(".\main_page\McCain-Logo.png")
        right_logo_label.setPixmap(right_logo_pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        top_layout.addWidget(right_logo_label, 0, Qt.AlignRight | Qt.AlignVCenter)
        
        # Add the top row to the main header layout
        header_main_layout.addLayout(top_layout)
        
        # Country and region selection area
        filter_layout = QHBoxLayout()
        filter_layout.setAlignment(Qt.AlignCenter)
        
        # Country selection
        country_label = QLabel("Select country:")
        country_label.setFont(get_body_font())
        
        self.country_combo = QComboBox()
        self.country_combo.setFont(get_body_font())
        self.country_combo.addItems(["Canada", "United States"])
        self.country_combo.setMinimumWidth(200)
        self.country_combo.setCurrentIndex(0)
        self.country_combo.currentIndexChanged.connect(self.on_country_changed)
        
        filter_layout.addWidget(country_label)
        filter_layout.addWidget(self.country_combo)
        
        # Add spacing between dropdowns
        filter_layout.addSpacing(20)
        
        # Region selection
        region_label = QLabel("Select region:")
        region_label.setFont(get_body_font())
        
        self.region_combo = QComboBox()
        self.region_combo.setFont(get_body_font())
        self.region_combo.addItem("None of the above")
        self.region_combo.setMinimumWidth(200)
        self.region_combo.setCurrentIndex(0)
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        
        self.update_regions_dropdown()
        
        filter_layout.addWidget(region_label)
        filter_layout.addWidget(self.region_combo)
        
        # Add the filter layout to header main layout
        header_main_layout.addLayout(filter_layout)
        header_main_layout.setAlignment(Qt.AlignCenter)
        
        # Add the header main layout to the ContentFrame
        header_frame.layout.addLayout(header_main_layout)
        
        # Add the header frame to the main layout
        main_layout.addWidget(header_frame)
        
        # Create the feature buttons
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        feature_buttons = [
            {
            "title": "Products List and Comparison",
            "description": "View and compare products with quick fact sheets\n",
            "page_index": 1
            },
            {
            "title": "EIQ Season Planner",
            "description": "Plan applications, Compare scenarios\nImport and work from previous years plans",
            "page_index": 2
            },
            {
            "title": "EIQ Calculator",
            "description": "Calculate Environmental Impact Quotients\nCompare EIQ of different applications",
            "page_index": 3
            }
        ]
        
        for info in feature_buttons:
            button = create_button(text=info["title"], description=info["description"], style="feature", callback=lambda checked=False, i=info["page_index"]: self.parent.navigate_to_page(i),parent=self)
            buttons_layout.addWidget(button)
        
        buttons_frame.layout.addLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)
        
        # Add a spacer before the info frames for better proportions
        main_layout.addStretch(1)
        
        # Info frame
        info_frame = ContentFrame()
        info_frame.setStyleSheet(INFO_TEXT_STYLE)
        info_layout = QVBoxLayout()
        
        # Warning title
        warning_title = QLabel("! ALWAYS CHECK LABELS !") 
        warning_title.setFont(get_subtitle_font(TITLE_FONT_SIZE))
        warning_title.setStyleSheet("color: red; font-weight: bold;")
        warning_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(warning_title)
                
        # EIQ info title
        info_title = QLabel("About Environmental Impact Quotient (EIQ)")
        info_title.setFont(get_subtitle_font())
        info_layout.addWidget(info_title)
        
        # EIQ description with concise information
        info_text = QLabel(
            "<b>Environmental Impact Quotient (EIQ)</b>, developed by the <b>NYSIPM Program at Cornell University</b>, "
            "provides a standardized assessment of pesticide environmental impact.<br><br>"
            "<b>EIQ evaluates three main components:</b><br>"
            "- <b>Farm worker risk</b> (applicator + harvester exposure)<br>"
            "- <b>Consumer risk</b> (food residue + groundwater effects)<br>"
            "- <b>Ecological risk</b> (fish, birds, bees, and beneficial insects)<br><br>"
            "Higher scores indicate greater environmental impact. The <b>Field Use EIQ</b> (= EIQ × %AI × Rate) "
            "adjusts for real-world application conditions, supporting sustainable pest management decisions.<br>"
            "ADD CONCISE EXPLANATION EIQ MOLECULE vs EIQ FIELD USE"
        )

        info_text.setWordWrap(True)
        info_text.setFont(get_body_font())
        info_layout.addWidget(info_text)
        
        info_frame.layout.addLayout(info_layout)
        main_layout.addWidget(info_frame)

    def get_regions_for_country(self, country):
        """Get region options for a specific country."""
        regions = {
            "United States": ["Washington", "Idaho", "Wisconsin", "Maine"],
            "Canada": ["New Brunswick", "Prince Edward Island", "Alberta", "Manitoba", "Quebec", "Saskatchewan"]
        }
        return regions.get(country, [])

    def update_regions_dropdown(self):
        """Update regions dropdown based on selected country."""
        current_region = self.region_combo.currentText()
        country = self.country_combo.currentText()
        
        # Clear and add default option
        self.region_combo.clear()
        self.region_combo.addItem("None of these")
        
        # Add country-specific regions
        self.region_combo.addItems(self.get_regions_for_country(country))
        
        # Try to restore previous selection if available
        index = self.region_combo.findText(current_region)
        self.region_combo.setCurrentIndex(max(0, index))  # Default to "None of these" if not found
    
    def on_country_changed(self, _):
        """Handle country selection change."""
        if self.initializing:
            return  # Skip during initialization
            
        country = self.country_combo.currentText()
        print(f"Country changed to: {country}")
        
        # Block signals during dropdown update to prevent cascading events
        self.region_combo.blockSignals(True)
        self.update_regions_dropdown()
        self.region_combo.blockSignals(False)
        
        # Get the new region value
        region = self.region_combo.currentText()
        
        # Emit signal for the country change
        self.country_changed.emit(country)
        
        # Also update the region in the parent window
        if self.parent and hasattr(self.parent, 'selected_region'):
            self.parent.selected_region = region
    
    def on_region_changed(self, _):
        """Handle region selection change."""
        if self.initializing:
            return  # Skip during initialization
                
        region = self.region_combo.currentText()
        print(f"Region changed to: {region}")
        
        # Emit signal with selected region - MainWindow handles filtering
        self.region_changed.emit(region)