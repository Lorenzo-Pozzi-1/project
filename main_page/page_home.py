"""
Unified Home Page for the LORENZO POZZI EIQ & STIR App

This module defines the UnifiedHomePage class which serves as the main navigation
screen for both EIQ and STIR features.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap

from common.constants import (
    get_margin_large, get_picture_size, 
    get_spacing_large, get_spacing_medium
)
from common.styles import (
    get_large_font, get_medium_font, 
    get_subtitle_font, get_title_font
)
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button
from main_page.widget_preferences_row import PreferencesRow


class HomePage(QWidget):
    """
    Home page with preferences management and navigation to both EIQ and STIR features.
    
    This page serves as the main entry point for users to access all features
    of the application including EIQ and STIR tools.
    """
    
    # Signals
    country_changed = Signal(str)
    region_changed = Signal(str)
    preferences_changed = Signal()
    
    def __init__(self, parent=None):
        """Initialize the home page."""
        super().__init__(parent)
        self.parent = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            get_margin_large(), get_margin_large(), 
            get_margin_large(), get_margin_large()
        )
        main_layout.setSpacing(get_spacing_large())
        
        # Add all UI components
        main_layout.addWidget(self._create_header_section())
        main_layout.addWidget(self._create_preferences_section())
        main_layout.addWidget(self._create_tools_section())
        main_layout.addStretch(1)
        main_layout.addWidget(self._create_learning_section())
    
    def _create_header_section(self):
        """Create the header section with logos and title."""
        header_frame = ContentFrame()
        header_layout = QVBoxLayout()
        
        # Create centered logos and title layout
        logos_title_layout = QHBoxLayout()
        logos_title_layout.setAlignment(Qt.AlignCenter)
        
        # Left logo
        left_logo = self._create_logo("main_page/logo_McCain.png")
        logos_title_layout.addWidget(left_logo)
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Title
        title_label = QLabel("RegenAg App")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        logos_title_layout.addWidget(title_label)
        logos_title_layout.addSpacing(get_spacing_medium())
        
        # Right logo
        right_logo = self._create_logo("main_page/logo_NAAg.png")
        logos_title_layout.addWidget(right_logo)
        
        header_layout.addLayout(logos_title_layout)
        header_frame.layout.addLayout(header_layout)
        
        return header_frame
    
    def _create_logo(self, logo_path):
        """Create a logo label with the specified image."""
        logo_label = QLabel()
        pixmap = QPixmap(resource_path(logo_path))
        logo_label.setPixmap(
            pixmap.scaled(
                get_picture_size(), get_picture_size(), 
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        return logo_label
    
    def _create_preferences_section(self):
        """Create the preferences section."""
        preferences_frame = ContentFrame()
        preferences_frame.setStyleSheet(
            """ContentFrame {
                background-color: white;
                border: 2px solid #FFD700;
                border-radius: 10px;
            }"""
        )
        
        # Create and configure preferences row
        self.preferences_row = PreferencesRow(self)
        self._connect_preferences_signals()
        
        preferences_frame.layout.addWidget(self.preferences_row)
        return preferences_frame
    
    def _connect_preferences_signals(self):
        """Connect signals from the preferences row."""
        self.preferences_row.country_changed.connect(self.on_country_changed)
        self.preferences_row.region_changed.connect(self.on_region_changed)
        self.preferences_row.preferences_changed.connect(self.on_preferences_changed)
    
    def _create_tools_section(self):
        """Create the main tools section with grid layout."""
        tools_frame = ContentFrame()
        tools_layout = QVBoxLayout()
        
        # Create grid layout for tools
        grid_layout = QGridLayout()
        grid_layout.setSpacing(get_spacing_large())
        
        # Add EIQ tools to grid (column 0)
        eiq_buttons = self._get_eiq_button_configs()
        for i, button_config in enumerate(eiq_buttons):
            button = self._create_feature_button(button_config)
            grid_layout.addWidget(button, i, 0)
        
        # Add STIR tools to grid (column 1)
        stir_buttons = self._get_stir_button_configs()
        for i, button_config in enumerate(stir_buttons):
            button = self._create_feature_button(button_config)
            grid_layout.addWidget(button, i, 1)
        
        tools_layout.addLayout(grid_layout)
        tools_frame.layout.addLayout(tools_layout)
        
        return tools_frame
    
    def _get_eiq_button_configs(self):
        """Get configuration for EIQ tool buttons."""
        return [
            {
                "title": "Products List and Comparison",
                "description": "View and compare products with quick fact sheets",
                "callback": lambda: self.parent.navigate_to_page(1)
            },
            {
                "title": "EIQ Season Planner",
                "description": "Plan applications, Compare scenarios\nImport and work from previous years plans",
                "callback": lambda: self.parent.navigate_to_page(2)
            },
            {
                "title": "EIQ Calculator",
                "description": "Calculate Environmental Impact Quotients\nCompare EIQ of different applications",
                "callback": lambda: self.parent.navigate_to_page(3)
            }
        ]
    
    def _get_stir_button_configs(self):
        """Get configuration for STIR tool buttons."""
        return [
            {
                "title": "STIR Calculator",
                "description": "Calculate Soil Tillage Intensity Ratings\nCompare different tillage practices",
                "callback": self.navigate_to_stir_calculator
            }
        ]
    
    def _create_feature_button(self, config):
        """Create a feature button from configuration."""
        return create_button(
            text=config["title"],
            description=config["description"],
            style="feature",
            callback=config["callback"],
            parent=self
        )
    
    def _create_learning_section(self):
        """Create the learning materials section."""
        learning_frame = ContentFrame()
        learning_layout = QHBoxLayout()
        learning_layout.setAlignment(Qt.AlignCenter)
        
        learning_button = create_button(
            text="Learning Materials",
            description="Learn about EIQ and STIR methodologies\nUnderstand regenerative agriculture practices",
            style="feature",
            callback=self.show_learning_materials,
            parent=self
        )
        learning_layout.addWidget(learning_button)
        
        learning_frame.layout.addLayout(learning_layout)
        return learning_frame
    
    # Public interface methods
    def navigate_to_stir_calculator(self):
        """Navigate directly to the STIR calculator page."""
        self.parent.navigate_to_page(5)

    def show_learning_materials(self):
        """Show the learning materials in the system browser."""
        self.parent.show_learning_materials()
    
    def set_country_region(self, country, region):
        """Set the country and region in the preferences row."""
        self.preferences_row.set_country_region(country, region)
            
    def load_preferences(self):
        """Load preferences into the preferences row."""
        self.preferences_row.load_preferences()

    def check_unsaved_preferences(self):
        """Check if there are unsaved preferences and ask user what to do."""
        if not self.preferences_row.has_unsaved_changes:
            return True
        
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
        else:
            self._discard_preferences_changes()
        
        return True
    
    def _discard_preferences_changes(self):
        """Discard unsaved preferences changes."""
        self.preferences_row.initializing = True
        self.preferences_row.load_preferences()
        self.preferences_row.initializing = False
        self.preferences_row.has_unsaved_changes = False
    
    # Signal handlers
    def on_country_changed(self, country):
        """Handle country change signal."""
        self.country_changed.emit(country)
        
    def on_region_changed(self, region):
        """Handle region change signal."""
        self.region_changed.emit(region)
    
    def on_preferences_changed(self):
        """Handle preferences changed signal."""
        self.preferences_changed.emit()