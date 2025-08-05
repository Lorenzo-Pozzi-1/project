"""
Home page for the LORENZO POZZI EIQ App

This module defines the HomePage class which serves as the main navigation
screen for the application.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from common.constants import get_margin_large, get_picture_size, get_spacing_large, get_spacing_medium
from common.styles import INFO_TEXT_STYLE, get_large_font, get_medium_font, get_subtitle_font, get_title_font
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button
from main_page.widget_preferences_row import PreferencesRow

class HomePage(QWidget):
    """
    Home page with preferences management and feature navigation buttons.
    
    This page serves as the main entry point for users to access the
    various features of the application.
    """
    
    country_changed = Signal(str)
    region_changed = Signal(str)
    preferences_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the home page."""
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(get_margin_large(), get_margin_large(), get_margin_large(), get_margin_large())
        main_layout.setSpacing(get_spacing_large())
        
        # Header with logos and title in its own ContentFrame
        header_frame = ContentFrame()
        
        # Create a layout for the entire header including back button
        header_main_layout = QVBoxLayout()
        
        # Top row with back button
        top_row_layout = QHBoxLayout()
        top_row_layout.setAlignment(Qt.AlignLeft)
        
        # Back button in top left
        back_button = create_button(
            text="← Back to Feature Selection", 
            style="white", 
            callback=self.go_back_to_feature_selection,
            parent=self
        )
        top_row_layout.addWidget(back_button)
        top_row_layout.addStretch()  # Push button to the left
        
        header_main_layout.addLayout(top_row_layout)
        
        # Logos and title row, centered together
        logos_title_layout = QHBoxLayout()
        logos_title_layout.setAlignment(Qt.AlignCenter)
        
        # Logo on the left
        left_logo_label = QLabel()
        pixmap = QPixmap(resource_path("main_page/logo_McCain.png"))
        left_logo_label.setPixmap(pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logos_title_layout.addWidget(left_logo_label)
        
        # Small spacing between logo and title
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Title in the center
        title_label = QLabel("EIQ")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        logos_title_layout.addWidget(title_label)
        
        # Small spacing between title and logo
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Logo on the right
        right_logo_label = QLabel()
        right_logo_pixmap = QPixmap(resource_path("main_page/logo_NAAg.png"))
        right_logo_label.setPixmap(right_logo_pixmap.scaled(get_picture_size(), get_picture_size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logos_title_layout.addWidget(right_logo_label)
        
        # Add logos and title layout to header main layout
        header_main_layout.addLayout(logos_title_layout)
        
        # Add header main layout to header frame
        header_frame.layout.addLayout(header_main_layout)
        
        # Add header frame to main layout
        main_layout.addWidget(header_frame)
        
        # Preferences row in its own ContentFrame
        preferences_frame = ContentFrame()
        preferences_frame.setStyleSheet("""ContentFrame {background-color: white;border: 2px solid #FFD700;border-radius: 10px;}""")
        # Create the preferences row
        self.preferences_row = PreferencesRow(self)
        
        # Connect signals from preferences row
        self.preferences_row.country_changed.connect(self.on_country_changed)
        self.preferences_row.region_changed.connect(self.on_region_changed)
        self.preferences_row.preferences_changed.connect(self.on_preferences_changed)
        
        # Add preferences row to preferences frame
        preferences_frame.layout.addWidget(self.preferences_row)
        
        # Add preferences frame to main layout
        main_layout.addWidget(preferences_frame)
        
        # Create the feature buttons
        buttons_frame = ContentFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(get_spacing_large())
        
        feature_buttons = [
            {
            "title": "Products List and Comparison",
            "description": "View and compare products with quick fact sheets\n",
            "page_index": 2
            },
            {
            "title": "EIQ Season Planner",
            "description": "Plan applications, Compare scenarios\nImport and work from previous years plans",
            "page_index": 3
            },
            {
            "title": "EIQ Calculator",
            "description": "Calculate Environmental Impact Quotients\nCompare EIQ of different applications",
            "page_index": 4
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
                
        # EIQ info title
        info_title = QLabel("Environmental Impact Quotients (EIQ) in a nutshell")
        info_title.setFont(get_subtitle_font())
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)
        
        # EIQ description with concise information
        info_text = QLabel(
            "EIQ scores are a tool to asses and compare pesticides' use impacts.<br>"
            "<b>Higher scores →  Higher impacts</b>.<br><br>"
            "Each Active Ingredient has an EIQ value, but we compare products based on the <b>Field Use EIQ</b>, where:<br>"
            "<b>Field Use EIQ = Active Ingredient EIQ x Active Ingredient concentration x Product Application Rate</b><br>"
            "EIQs evaluate the risk posed by an active ingredient to non-target beings:<br>"
            "Farm worker risk &nbsp;&nbsp;&nbsp; Consumer risk &nbsp;&nbsp;&nbsp; Ecological risk"
        )

        info_text.setWordWrap(True)
        info_text.setFont(get_large_font())
        info_text.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_text)
        
        # Cornell NYSIPM link
        cornell_link_text = QLabel('Learn more on the <a href="https://cals.cornell.edu/integrated-pest-management/risk-assessment/eiq">Cornell IPM website</a>')
        cornell_link_text.setFont(get_large_font())
        cornell_link_text.setAlignment(Qt.AlignCenter)
        cornell_link_text.setOpenExternalLinks(True)
        cornell_link_text.setTextFormat(Qt.RichText)
        info_layout.addWidget(cornell_link_text)

        # Warning text
        warning_text = QLabel("Always double check product labels and SDS before using a product. This app is an aide, not a substitute for professional advice.") 
        warning_text.setFont(get_large_font())
        warning_text.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(warning_text)

        info_frame.layout.addLayout(info_layout)
        main_layout.addWidget(info_frame)

    def go_back_to_feature_selection(self):
        """Navigate back to the feature selection page."""
        self.parent.navigate_to_page(0)  # Feature selection page is at index 0

    def on_country_changed(self, country):
        """Forward country change signal."""
        self.country_changed.emit(country)
        
    def on_region_changed(self, region):
        """Forward region change signal."""
        self.region_changed.emit(region)
    
    def on_preferences_changed(self):
        """Forward preferences changed signal."""
        self.preferences_changed.emit()

    def set_country_region(self, country, region):
        """Set the country and region in the preferences row."""
        self.preferences_row.set_country_region(country, region)
            
    def load_preferences(self):
        """Load preferences into the preferences row."""
        self.preferences_row.load_preferences()

    def check_unsaved_preferences(self):
        """Check if there are unsaved preferences and ask user what to do."""
        if self.preferences_row.has_unsaved_changes:
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("Unsaved edits to the preferences,\nwhat to do with these edits?")
            msg_box.setIcon(QMessageBox.Warning)
            
            save_button = msg_box.addButton("Save", QMessageBox.AcceptRole)
            discard_button = msg_box.addButton("Discard", QMessageBox.RejectRole)
            
            msg_box.setFont(get_medium_font())
            msg_box.exec()
            
            if msg_box.clickedButton() == save_button:
                self.preferences_row.save_preferences()
                return True
            else:
                # Reload the preferences to discard changes
                self.preferences_row.initializing = True
                self.preferences_row.load_preferences()
                self.preferences_row.initializing = False
                self.preferences_row.has_unsaved_changes = False
                return True
        
        return True  # No unsaved changes, can proceed