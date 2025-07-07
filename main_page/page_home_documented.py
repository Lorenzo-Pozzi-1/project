"""
Home Page Module for PestIQ Application

This module implements the main landing page for the PestIQ application, providing
user navigation to different features and preferences management.

Author: Lorenzo Pozzi
Created: 2024
Framework: PySide6 (Qt for Python)
Purpose: Environmental Impact Quotient (EIQ) calculation and pesticide management

Classes:
    HomePage: Main home page widget with navigation and preferences

Dependencies:
    - PySide6: GUI framework
    - common.constants: Application-wide constants for UI spacing and sizing
    - common.styles: Styling constants and font functions
    - common.utils: Utility functions including resource path management
    - common.widgets.header_frame_buttons: Custom UI components
    - main_page.widget_preferences_row: User preferences management widget

UI Structure:
    ┌─────────────────────────────────────────┐
    │ Header (Logos + Title)                  │
    ├─────────────────────────────────────────┤
    │ Preferences Row (Country/Region)        │
    ├─────────────────────────────────────────┤
    │ Feature Navigation Buttons              │
    │ - Products List & Comparison            │
    │ - EIQ Season Planner                    │
    │ - EIQ Calculator                        │
    ├─────────────────────────────────────────┤
    │ Information Section                     │
    │ - EIQ explanation                       │
    │ - External links                        │
    │ - Disclaimers                           │
    └─────────────────────────────────────────┘
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from common.constants import get_margin_large, get_picture_size, get_spacing_large, get_spacing_medium
from common.styles import INFO_TEXT_STYLE, PREFERENCES_FRAME_STYLE, get_large_font, get_medium_font, get_subtitle_font, get_title_font
from common.utils import resource_path
from common.widgets.header_frame_buttons import ContentFrame, create_button
from main_page.widget_preferences_row import PreferencesRow


class HomePage(QWidget):
    """
    Main home page widget for the PestIQ application.
    
    This class creates the landing page that users see when they first open the
    application. It provides navigation to the main features and handles user
    preferences for country and region settings.
    
    Attributes:
        parent: Reference to the parent widget (typically the main window)
        preferences_row (PreferencesRow): Widget for managing user preferences
        
    Signals:
        country_changed (Signal[str]): Emitted when user changes country preference
        region_changed (Signal[str]): Emitted when user changes region preference  
        preferences_changed (Signal): Emitted when any preference is modified
        
    UI Components:
        - Header with McCain Foods and North American Agriculture logos
        - Application title
        - User preferences selection (country/region)
        - Three main feature navigation buttons
        - Educational information about EIQ (Environmental Impact Quotients)
        - External links and disclaimers
        
    Navigation Targets:
        - Page 1: Products List and Comparison
        - Page 2: EIQ Season Planner
        - Page 3: EIQ Calculator
    """
    
    # Signal definitions with type annotations for clarity
    country_changed = Signal(str)  # Emitted with country code (e.g., "CA", "US")
    region_changed = Signal(str)   # Emitted with region code (e.g., "AB", "ID")
    preferences_changed = Signal() # General notification of preference changes
    
    def __init__(self, parent=None):
        """
        Initialize the home page widget.
        
        Args:
            parent (QWidget, optional): Parent widget, typically the main window.
                                      Defaults to None.
                                      
        Side Effects:
            - Sets up the complete UI layout
            - Connects signal handlers for preferences management
            - Initializes all child widgets
        """
        super().__init__(parent)
        self.parent = parent
        self.setup_ui()
    
    def setup_ui(self):
        """
        Create and configure all UI components for the home page.
        
        This method builds the complete UI hierarchy using a vertical layout
        with the following sections:
        1. Header (logos and title)
        2. Preferences management
        3. Feature navigation buttons
        4. Educational content about EIQ
        
        Layout Strategy:
            - Uses ContentFrame widgets for consistent styling
            - Applies spacing and margins from common.constants
            - Uses signal-slot pattern for inter-component communication
            
        UI Framework Details:
            - Main layout: QVBoxLayout with large margins and spacing
            - Header layout: QHBoxLayout with center alignment
            - Button layout: QHBoxLayout with equal spacing
            - Info layout: QVBoxLayout for text content
            
        Resource Dependencies:
            - main_page/logo_McCain.png: McCain Foods logo
            - main_page/logo_NAAg.png: North American Agriculture logo
        """
        # Main layout configuration
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(
            get_margin_large(),  # left
            get_margin_large(),  # top  
            get_margin_large(),  # right
            get_margin_large()   # bottom
        )
        main_layout.setSpacing(get_spacing_large())
        
        # ===== HEADER SECTION =====
        # Contains logos and application title in a centered layout
        header_frame = ContentFrame()
        
        # Create horizontal layout for logos and title
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)
        
        # Left logo (McCain Foods)
        left_logo_label = QLabel()
        left_logo_label.setObjectName("mccain_logo")  # For testing/debugging
        pixmap = QPixmap(resource_path("main_page/logo_McCain.png"))
        if pixmap.isNull():
            # Fallback if logo not found
            left_logo_label.setText("McCain Foods")
            left_logo_label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        else:
            left_logo_label.setPixmap(
                pixmap.scaled(
                    get_picture_size(),
                    get_picture_size(), 
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        top_layout.addWidget(left_logo_label)
        
        # Spacing between logo and title
        top_layout.addSpacing(get_spacing_medium())
        
        # Application title
        title_label = QLabel("Pesticides App")
        title_label.setObjectName("app_title")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(get_title_font())
        top_layout.addWidget(title_label)
        
        # Spacing between title and right logo
        top_layout.addSpacing(get_spacing_medium())
        
        # Right logo (North American Agriculture)
        right_logo_label = QLabel()
        right_logo_label.setObjectName("naag_logo")
        right_logo_pixmap = QPixmap(resource_path("main_page/logo_NAAg.png"))
        if right_logo_pixmap.isNull():
            # Fallback if logo not found
            right_logo_label.setText("NA Agriculture")
            right_logo_label.setStyleSheet("border: 1px solid gray; padding: 10px;")
        else:
            right_logo_label.setPixmap(
                right_logo_pixmap.scaled(
                    get_picture_size(),
                    get_picture_size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
        top_layout.addWidget(right_logo_label)
        
        # Add header layout to frame and main layout
        header_frame.layout.addLayout(top_layout)
        main_layout.addWidget(header_frame)
        
        # ===== PREFERENCES SECTION =====
        # User preferences for country and region selection
        preferences_frame = ContentFrame()
        preferences_frame.setStyleSheet(PREFERENCES_FRAME_STYLE)
        preferences_frame.setObjectName("preferences_frame")
        
        # Create preferences row widget
        self.preferences_row = PreferencesRow(self)
        
        # Connect preference change signals to local handlers
        # These handlers will re-emit the signals to parent components
        self.preferences_row.country_changed.connect(self.on_country_changed)
        self.preferences_row.region_changed.connect(self.on_region_changed)
        self.preferences_row.preferences_changed.connect(self.on_preferences_changed)
        
        # Add preferences widget to frame
        preferences_frame.layout.addWidget(self.preferences_row)
        main_layout.addWidget(preferences_frame)
        
        # ===== FEATURE NAVIGATION SECTION =====
        # Buttons for accessing main application features
        buttons_frame = ContentFrame()
        buttons_frame.setObjectName("navigation_frame")
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(get_spacing_large())
        
        # Feature button configuration
        # Each button navigates to a different page in the application
        feature_buttons = [
            {
                "title": "Products List and Comparison",
                "description": "View and compare products with quick fact sheets\n",
                "page_index": 1,  # Navigation target
                "object_name": "products_button"
            },
            {
                "title": "EIQ Season Planner", 
                "description": "Plan applications, Compare scenarios\nImport and work from previous years plans",
                "page_index": 2,
                "object_name": "planner_button"
            },
            {
                "title": "EIQ Calculator",
                "description": "Calculate Environmental Impact Quotients\nCompare EIQ of different applications", 
                "page_index": 3,
                "object_name": "calculator_button"
            }
        ]
        
        # Create navigation buttons dynamically
        for info in feature_buttons:
            # Create button with callback that navigates to specified page
            # Lambda captures page_index to avoid late binding issues
            button = create_button(
                text=info["title"],
                description=info["description"],
                style="feature",
                callback=lambda checked=False, i=info["page_index"]: self._navigate_to_page(i),
                parent=self
            )
            button.setObjectName(info.get("object_name", f"button_{info['page_index']}"))
            buttons_layout.addWidget(button)
        
        buttons_frame.layout.addLayout(buttons_layout)
        main_layout.addWidget(buttons_frame)
        
        # Add flexible space to push info section toward bottom
        main_layout.addStretch(1)
        
        # ===== INFORMATION SECTION =====
        # Educational content about Environmental Impact Quotients
        info_frame = ContentFrame()
        info_frame.setStyleSheet(INFO_TEXT_STYLE)
        info_frame.setObjectName("info_frame")
        info_layout = QVBoxLayout()
        
        # Section title
        info_title = QLabel("Environmental Impact Quotients (EIQ) in a nutshell")
        info_title.setObjectName("eiq_title")
        info_title.setFont(get_subtitle_font())
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)
        
        # Main explanation text with HTML formatting
        info_text = QLabel(
            "EIQ scores are a tool to asses and compare pesticides' use impacts.<br>"
            "<b>Higher scores →  Higher impacts</b>.<br><br>"
            "Each Active Ingredient has an EIQ value, but we compare products based on the <b>Field Use EIQ</b>, where:<br>"
            "<b>Field Use EIQ = Active Ingredient EIQ x Active Ingredient concentration x Product Application Rate</b><br>"
            "EIQs evaluate the risk posed by an active ingredient to non-target beings:<br>"
            "Farm worker risk &nbsp;&nbsp;&nbsp; Consumer risk &nbsp;&nbsp;&nbsp; Ecological risk"
        )
        info_text.setObjectName("eiq_description")
        info_text.setWordWrap(True)
        info_text.setFont(get_large_font())
        info_text.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_text)
        
        # External link to Cornell University IPM website
        cornell_link_text = QLabel(
            'Learn more on the <a href="https://cals.cornell.edu/integrated-pest-management/risk-assessment/eiq">Cornell IPM website</a>'
        )
        cornell_link_text.setObjectName("cornell_link")
        cornell_link_text.setFont(get_large_font())
        cornell_link_text.setAlignment(Qt.AlignCenter)
        cornell_link_text.setOpenExternalLinks(True)  # Enable clickable links
        cornell_link_text.setTextFormat(Qt.RichText)   # Enable HTML formatting
        info_layout.addWidget(cornell_link_text)

        # Disclaimer text
        warning_text = QLabel(
            "Always double check product labels and SDS before using a product. "
            "This app is an aide, not a substitute for professional advice."
        )
        warning_text.setObjectName("disclaimer_text")
        warning_text.setFont(get_large_font())
        warning_text.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(warning_text)

        # Add info section to main layout
        info_frame.layout.addLayout(info_layout)
        main_layout.addWidget(info_frame)

    def _navigate_to_page(self, page_index):
        """
        Navigate to the specified page index.
        
        This is a helper method that safely calls the parent's navigation method.
        
        Args:
            page_index (int): Index of the page to navigate to
                            1 = Products page
                            2 = Season Planner page  
                            3 = Calculator page
                            
        Side Effects:
            - Calls parent.navigate_to_page() if parent exists
            - May trigger page transitions and UI state changes
        """
        if self.parent and hasattr(self.parent, 'navigate_to_page'):
            self.parent.navigate_to_page(page_index)

    def on_country_changed(self, country):
        """
        Handle country preference changes.
        
        This slot receives country change notifications from the preferences row
        and forwards them to any connected listeners.
        
        Args:
            country (str): ISO country code (e.g., "CA" for Canada, "US" for United States)
            
        Emits:
            country_changed: Signal with the new country code
            
        Usage:
            Connected automatically in setup_ui(). External components can
            connect to the country_changed signal to respond to changes.
        """
        self.country_changed.emit(country)
        
    def on_region_changed(self, region):
        """
        Handle region preference changes.
        
        This slot receives region change notifications from the preferences row
        and forwards them to any connected listeners.
        
        Args:
            region (str): Region/state/province code (e.g., "AB" for Alberta, "ID" for Idaho)
            
        Emits:
            region_changed: Signal with the new region code
            
        Usage:
            Connected automatically in setup_ui(). External components can
            connect to the region_changed signal to respond to changes.
        """
        self.region_changed.emit(region)
    
    def on_preferences_changed(self):
        """
        Handle general preference changes.
        
        This slot receives generic preference change notifications and forwards
        them to any connected listeners. Used for UI updates and data refreshing.
        
        Emits:
            preferences_changed: Signal indicating preferences have been modified
            
        Usage:
            Connected automatically in setup_ui(). Used to trigger data reloading
            in other parts of the application when user preferences change.
        """
        self.preferences_changed.emit()

    def set_country_region(self, country, region):
        """
        Programmatically set the country and region preferences.
        
        This method allows external code to update the user's preferences
        without user interaction, such as when loading saved settings.
        
        Args:
            country (str): ISO country code to set
            region (str): Region/state/province code to set
            
        Side Effects:
            - Updates the preferences row UI components
            - May trigger preference change signals
            - Updates internal state of preferences widgets
            
        Example:
            homepage.set_country_region("CA", "AB")  # Set to Canada, Alberta
        """
        self.preferences_row.set_country_region(country, region)
            
    def load_preferences(self):
        """
        Load user preferences from persistent storage.
        
        This method triggers the preferences row to load saved user preferences
        from the application's configuration file or database.
        
        Side Effects:
            - Reads from user_preferences.json or similar storage
            - Updates UI components with saved values
            - May trigger preference change signals
            
        Usage:
            Typically called during application startup or when refreshing
            user settings from storage.
        """
        self.preferences_row.load_preferences()

    def check_unsaved_preferences(self):
        """
        Check for unsaved preference changes and handle user decision.
        
        This method displays a dialog to users when they have made changes
        to their preferences but haven't saved them. It gives them the option
        to save or discard the changes.
        
        Returns:
            bool: True if the operation can proceed (changes saved or discarded),
                  False if the user cancelled the operation
                  
        Dialog Options:
            - Save: Persist changes and continue
            - Discard: Revert changes and continue
            
        Side Effects:
            - May display a QMessageBox dialog
            - May save preferences to storage
            - May reload preferences from storage (on discard)
            - Updates internal state flags
            
        Usage:
            Called before navigating away from the home page or closing
            the application to prevent data loss.
            
        Example:
            if not homepage.check_unsaved_preferences():
                return  # User cancelled, don't proceed with navigation
        """
        if self.preferences_row.has_unsaved_changes:
            # Create and configure warning dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Unsaved Changes")
            msg_box.setText("Unsaved edits to the preferences,\nwhat to do with these edits?")
            msg_box.setIcon(QMessageBox.Warning)
            
            # Add custom buttons with appropriate roles
            save_button = msg_box.addButton("Save", QMessageBox.AcceptRole)
            discard_button = msg_box.addButton("Discard", QMessageBox.RejectRole)
            
            # Apply consistent styling
            msg_box.setFont(get_medium_font())
            msg_box.exec()
            
            # Handle user choice
            if msg_box.clickedButton() == save_button:
                # Save changes and continue
                self.preferences_row.save_preferences()
                return True
            else:
                # Discard changes by reloading from storage
                self.preferences_row.initializing = True  # Prevent change signals
                self.preferences_row.load_preferences()
                self.preferences_row.initializing = False
                self.preferences_row.has_unsaved_changes = False
                return True
        
        # No unsaved changes, operation can proceed
        return True
