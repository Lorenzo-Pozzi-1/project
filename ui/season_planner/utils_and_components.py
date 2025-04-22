"""
Shared utilities and UI components for the Season Planner module.

This module provides reusable UI components and utility functions 
specific to the Season Planner functionality.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QDateEdit, QDoubleSpinBox, QComboBox, QPushButton, 
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView,
    QSpinBox, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QDate
from PySide6.QtGui import QColor, QBrush

from ui.common.styles import (
    get_subtitle_font, get_body_font, SPACING_MEDIUM, PRIMARY_BUTTON_STYLE,
    SECONDARY_BUTTON_STYLE, EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)
from ui.common.widgets import ContentFrame

from data.products_data import load_products

# Import models
from ui.season_planner.models import Product, Application, Season


class ApplicationEditor(QWidget):
    """
    Editor widget for creating and editing applications.
    
    This component allows selecting products, setting application details,
    and calculating EIQ.
    """
    
    application_updated = Signal(Application)
    
    def __init__(self, parent=None, application=None):
        """
        Initialize the application editor.
        
        Args:
            parent: Parent widget
            application: Optional existing Application to edit
        """
        super().__init__(parent)
        
        self.parent = parent
        self.application = application or Application()
        self.products_data = []
        
        self.setup_ui()
        self.load_products_data()
        
        # Populate fields with existing data if editing
        if application:
            self.populate_fields()
    
    def setup_ui(self):
        """Set up the UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Application details frame
        details_frame = QFrame()
        details_frame.setFrameShape(QFrame.StyledPanel)
        details_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px;")
        details_layout = QVBoxLayout(details_frame)
        
        # Title
        title = QLabel("Application Details")
        title.setFont(get_subtitle_font(size=16))
        details_layout.addWidget(title)
        
        # Application date and field
        date_field_layout = QHBoxLayout()
        
        # Date
        date_label = QLabel("Date:")
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        date_field_layout.addWidget(date_label)
        date_field_layout.addWidget(self.date_edit)
        
        # Field
        field_label = QLabel("Field:")
        self.field_input = QLineEdit()
        self.field_input.setPlaceholderText("Enter field name")
        date_field_layout.addWidget(field_label)
        date_field_layout.addWidget(self.field_input)
        
        details_layout.addLayout(date_field_layout)
        
        # Area and application method
        area_method_layout = QHBoxLayout()
        
        # Area
        area_label = QLabel("Area:")
        self.area_spin = QDoubleSpinBox()
        self.area_spin.setRange(0.1, 10000.0)
        self.area_spin.setValue(1.0)
        self.area_spin.setDecimals(2)
        
        self.area_unit_combo = QComboBox()
        self.area_unit_combo.addItems(["ha", "acre"])
        
        area_method_layout.addWidget(area_label)
        area_method_layout.addWidget(self.area_spin)
        area_method_layout.addWidget(self.area_unit_combo)
        
        # Application method
        method_label = QLabel("Method:")
        self.method_combo = QComboBox()
        self.method_combo.addItems([
            "Foliar", "Soil", "Furrow", "Broadcast", "Chemigation", 
            "Aerial", "Spot Treatment", "Other"
        ])
        area_method_layout.addWidget(method_label)
        area_method_layout.addWidget(self.method_combo)
        
        details_layout.addLayout(area_method_layout)
        
        # Products section
        products_title = QLabel("Products")
        products_title.setFont(get_subtitle_font(size=14))
        details_layout.addWidget(products_title)
        
        # Products table
        self.products_table = QTableWidget(0, 7)
        self.products_table.setHorizontalHeaderLabels([
            "Product", "Type", "Active Ingredient", "AI %", 
            "EIQ", "Rate", "Unit"
        ])
        
        # Set column widths
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        details_layout.addWidget(self.products_table)
        
        # Add product button
        add_product_button = QPushButton("Add Product")
        add_product_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_product_button.clicked.connect(self.add_product_row)
        details_layout.addWidget(add_product_button, alignment=Qt.AlignRight)
        
        # Notes section
        notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Enter any notes about this application")
        details_layout.addWidget(notes_label)
        details_layout.addWidget(self.notes_input)
        
        # EIQ results
        eiq_layout = QHBoxLayout()
        eiq_label = QLabel("Total Field EIQ:")
        eiq_label.setFont(get_body_font(size=14, bold=True))
        
        self.eiq_result = QLabel("0.0")
        self.eiq_result.setFont(get_body_font(size=16, bold=True))
        
        eiq_layout.addWidget(eiq_label)
        eiq_layout.addWidget(self.eiq_result)
        eiq_layout.addStretch()
        
        details_layout.addLayout(eiq_layout)
        
        main_layout.addWidget(details_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Application")
        self.save_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        self.save_button.clicked.connect(self.save_application)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        self.cancel_button.clicked.connect(self.cancel_edit)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_products_data(self):
        """Load products data for product selection."""
        self.products_data = load_products()
    
    def populate_fields(self):
        """Populate fields with data from the application being edited."""
        # Set application details
        self.date_edit.setDate(QDate(
            self.application.date.year,
            self.application.date.month,
            self.application.date.day
        ))
        self.field_input.setText(self.application.field_name)
        self.area_spin.setValue(self.application.area)
        
        # Set area unit
        index = self.area_unit_combo.findText(self.application.area_unit)
        if index >= 0:
            self.area_unit_combo.setCurrentIndex(index)
        
        # Set application method
        method_index = self.method_combo.findText(self.application.application_method)
        if method_index >= 0:
            self.method_combo.setCurrentIndex(method_index)
        
        # Set notes
        self.notes_input.setText(self.application.notes)
        
        # Add products
        for product in self.application.products:
            self.add_product_row(product)
        
        # Update EIQ
        self.update_eiq_calculation()
    
    def add_product_row(self, product=None):
        """
        Add a new product row to the table.
        
        Args:
            product: Optional Product to populate the row with
        """
        row = self.products_table.rowCount()
        self.products_table.insertRow(row)
        
        # Product selection combo
        product_combo = QComboBox()
        product_combo.addItem("Select a product...", None)
        
        # Populate with products from database
        for p in self.products_data:
            product_combo.addItem(p.product_name, p)
        
        # Connect selection change
        product_combo.currentIndexChanged.connect(
            lambda idx, r=row: self.product_selected(r, idx)
        )
        
        self.products_table.setCellWidget(row, 0, product_combo)
        
        # Empty cells for other fields
        for col in range(1, 4):
            self.products_table.setItem(row, col, QTableWidgetItem(""))
        
        # EIQ value (read-only)
        eiq_item = QTableWidgetItem("0.0")
        eiq_item.setFlags(eiq_item.flags() & ~Qt.ItemIsEditable)
        self.products_table.setItem(row, 4, eiq_item)
        
        # Application rate spinner
        rate_spin = QDoubleSpinBox()
        rate_spin.setRange(0.01, 1000.0)
        rate_spin.setValue(1.0)
        rate_spin.valueChanged.connect(self.update_eiq_calculation)
        self.products_table.setCellWidget(row, 5, rate_spin)
        
        # Unit combo
        unit_combo = QComboBox()
        unit_combo.addItems([
            "kg/ha", "g/ha", "l/ha", "ml/ha", 
            "lbs/acre", "oz/acre", "fl oz/acre", "qt/acre", "pt/acre"
        ])
        unit_combo.currentIndexChanged.connect(self.update_eiq_calculation)
        self.products_table.setCellWidget(row, 6, unit_combo)
        
        # If we have a product, populate the row
        if product:
            # Find the product in the combo
            for i in range(product_combo.count()):
                combo_product = product_combo.itemData(i)
                if combo_product and combo_product.product_name == product.name:
                    product_combo.setCurrentIndex(i)
                    break
            
            # Set other fields
            self.products_table.setItem(row, 1, QTableWidgetItem(product.type))
            self.products_table.setItem(row, 2, QTableWidgetItem(product.active_ingredient))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product.ai_percentage)))
            self.products_table.setItem(row, 4, QTableWidgetItem(str(product.eiq_value)))
            
            # Set rate
            rate_spin.setValue(product.application_rate)
            
            # Set unit
            unit_index = unit_combo.findText(product.rate_unit)
            if unit_index >= 0:
                unit_combo.setCurrentIndex(unit_index)
    
    def product_selected(self, row, index):
        """
        Handle product selection change.
        
        Args:
            row: Row index in the table
            index: Selected index in the combo box
        """
        combo = self.products_table.cellWidget(row, 0)
        selected_product = combo.itemData(index)
        
        if not selected_product:
            # Clear the row
            self.products_table.setItem(row, 1, QTableWidgetItem(""))
            self.products_table.setItem(row, 2, QTableWidgetItem(""))
            self.products_table.setItem(row, 3, QTableWidgetItem(""))
            self.products_table.setItem(row, 4, QTableWidgetItem("0.0"))
        else:
            # Set product info
            self.products_table.setItem(row, 1, QTableWidgetItem(selected_product.product_type))
            
            # Active ingredient (use first one)
            ai_name = selected_product.ai1 or ""
            self.products_table.setItem(row, 2, QTableWidgetItem(ai_name))
            
            # AI percentage
            ai_percent = selected_product.ai1_concentration_percent
            if ai_percent is not None:
                self.products_table.setItem(row, 3, QTableWidgetItem(str(ai_percent)))
            else:
                self.products_table.setItem(row, 3, QTableWidgetItem(""))
            
            # EIQ value
            eiq = selected_product.ai1_eiq
            if eiq is not None:
                self.products_table.setItem(row, 4, QTableWidgetItem(str(eiq)))
            else:
                self.products_table.setItem(row, 4, QTableWidgetItem("0.0"))
            
            # Set rate to suggested rate if available
            rate_spin = self.products_table.cellWidget(row, 5)
            if selected_product.label_suggested_rate:
                rate_spin.setValue(selected_product.label_suggested_rate)
            elif selected_product.label_maximum_rate:
                rate_spin.setValue(selected_product.label_maximum_rate)
            elif selected_product.label_minimum_rate:
                rate_spin.setValue(selected_product.label_minimum_rate)
            
            # Set unit if available
            unit_combo = self.products_table.cellWidget(row, 6)
            if selected_product.rate_uom:
                index = unit_combo.findText(selected_product.rate_uom)
                if index >= 0:
                    unit_combo.setCurrentIndex(index)
        
        # Update the EIQ calculation
        self.update_eiq_calculation()
    
    def update_eiq_calculation(self):
        """Update the EIQ calculation based on current values."""
        total_eiq = 0.0
        
        for row in range(self.products_table.rowCount()):
            # Get EIQ value
            eiq_item = self.products_table.item(row, 4)
            ai_percent_item = self.products_table.item(row, 3)
            
            if not eiq_item or not ai_percent_item:
                continue
            
            try:
                eiq = float(eiq_item.text())
                ai_percent = float(ai_percent_item.text())
                
                # Get application rate
                rate_spin = self.products_table.cellWidget(row, 5)
                if not rate_spin:
                    continue
                rate = rate_spin.value()
                
                # Get unit
                unit_combo = self.products_table.cellWidget(row, 6)
                if not unit_combo:
                    continue
                unit = unit_combo.currentText()
                
                # Convert to decimal
                ai_decimal = ai_percent / 100.0
                
                # Convert rate based on unit (assuming base unit is kg/ha)
                rate_factor = 1.0
                if 'g/ha' in unit:
                    rate_factor = 0.001  # g to kg
                elif 'ml/ha' in unit:
                    rate_factor = 0.001  # ml to l (assuming density of 1)
                elif 'lbs/acre' in unit:
                    rate_factor = 1.12  # lbs/acre to kg/ha
                elif 'oz/acre' in unit:
                    rate_factor = 0.07  # oz/acre to kg/ha
                elif 'fl oz/acre' in unit:
                    rate_factor = 0.07  # fl oz/acre to kg/ha
                elif 'qt/acre' in unit:
                    rate_factor = 2.24  # qt/acre to kg/ha
                elif 'pt/acre' in unit:
                    rate_factor = 1.12  # pt/acre to kg/ha
                
                # Calculate Field EIQ for this product
                product_eiq = eiq * ai_decimal * rate * rate_factor
                total_eiq += product_eiq
                
            except (ValueError, TypeError):
                # Skip rows with invalid values
                continue
        
        # Update the EIQ result
        self.eiq_result.setText(f"{total_eiq:.2f}")
        
        # Color code based on EIQ value
        if total_eiq < 20:
            self.eiq_result.setStyleSheet("color: #009863;")  # Green
        elif total_eiq < 50:
            self.eiq_result.setStyleSheet("color: #fee000;")  # Yellow
        else:
            self.eiq_result.setStyleSheet("color: #EC3400;")  # Red
    
    def get_application_from_fields(self):
        """
        Create an Application object from the current field values.
        
        Returns:
            Application: The created Application object
        """
        # Get date
        qdate = self.date_edit.date()
        date = datetime.date(qdate.year(), qdate.month(), qdate.day())
        
        # Create Application object
        application = Application(
            id=self.application.id,  # Keep original ID if editing
            date=date,
            field_name=self.field_input.text(),
            area=self.area_spin.value(),
            area_unit=self.area_unit_combo.currentText(),
            application_method=self.method_combo.currentText(),
            notes=self.notes_input.text()
        )
        
        # Add products
        for row in range(self.products_table.rowCount()):
            product_combo = self.products_table.cellWidget(row, 0)
            if not product_combo or product_combo.currentIndex() == 0:
                continue
            
            type_item = self.products_table.item(row, 1)
            ai_item = self.products_table.item(row, 2)
            ai_percent_item = self.products_table.item(row, 3)
            eiq_item = self.products_table.item(row, 4)
            
            # Get rate and unit
            rate_spin = self.products_table.cellWidget(row, 5)
            unit_combo = self.products_table.cellWidget(row, 6)
            
            if (not type_item or not ai_item or not ai_percent_item or 
                not eiq_item or not rate_spin or not unit_combo):
                continue
            
            try:
                product = Product(
                    name=product_combo.currentText(),
                    type=type_item.text(),
                    active_ingredient=ai_item.text(),
                    ai_percentage=float(ai_percent_item.text()),
                    eiq_value=float(eiq_item.text()),
                    application_rate=rate_spin.value(),
                    rate_unit=unit_combo.currentText()
                )
                application.add_product(product)
            except (ValueError, TypeError):
                # Skip products with invalid values
                continue
        
        return application
    
    def save_application(self):
        """Save the application and emit update signal."""
        application = self.get_application_from_fields()
        
        # Emit signal with updated application
        self.application_updated.emit(application)
    
    def cancel_edit(self):
        """Cancel editing and go back."""
        # Notify parent
        if hasattr(self.parent, "cancel_application_edit"):
            self.parent.cancel_application_edit()


class SeasonSummary(QWidget):
    """
    Widget displaying season summary information.
    
    Shows total EIQ, application count, and other summary statistics.
    """
    
    def __init__(self, parent=None):
        """Initialize the season summary widget."""
        super().__init__(parent)
        self.parent = parent
        self.season = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Summary frame
        summary_frame = ContentFrame()
        summary_layout = QVBoxLayout()
        
        # Title
        title = QLabel("Season Summary")
        title.setFont(get_subtitle_font(size=16))
        summary_layout.addWidget(title)
        
        # Create a grid for summary statistics
        grid_layout = QHBoxLayout()
        grid_layout.setSpacing(30)
        
        # Season EIQ
        eiq_layout = QVBoxLayout()
        eiq_title = QLabel("Total EIQ")
        eiq_title.setAlignment(Qt.AlignCenter)
        self.eiq_value = QLabel("0.0")
        self.eiq_value.setFont(get_subtitle_font(size=24))
        self.eiq_value.setAlignment(Qt.AlignCenter)
        eiq_layout.addWidget(eiq_title)
        eiq_layout.addWidget(self.eiq_value)
        grid_layout.addLayout(eiq_layout)
        
        # Application count
        apps_layout = QVBoxLayout()
        apps_title = QLabel("Applications")
        apps_title.setAlignment(Qt.AlignCenter)
        self.apps_value = QLabel("0")
        self.apps_value.setFont(get_subtitle_font(size=24))
        self.apps_value.setAlignment(Qt.AlignCenter)
        apps_layout.addWidget(apps_title)
        apps_layout.addWidget(self.apps_value)
        grid_layout.addLayout(apps_layout)
        
        # Products count
        products_layout = QVBoxLayout()
        products_title = QLabel("Products Used")
        products_title.setAlignment(Qt.AlignCenter)
        self.products_value = QLabel("0")
        self.products_value.setFont(get_subtitle_font(size=24))
        self.products_value.setAlignment(Qt.AlignCenter)
        products_layout.addWidget(products_title)
        products_layout.addWidget(self.products_value)
        grid_layout.addLayout(products_layout)
        
        summary_layout.addLayout(grid_layout)
        
        # Impact rating
        self.impact_label = QLabel("Low Environmental Impact")
        self.impact_label.setFont(get_body_font(size=14, bold=True))
        self.impact_label.setAlignment(Qt.AlignCenter)
        self.impact_label.setStyleSheet("padding: 10px; border-radius: 5px; background-color: #E6F5E6;")
        summary_layout.addWidget(self.impact_label)
        
        summary_frame.layout.addLayout(summary_layout)
        main_layout.addWidget(summary_frame)
    
    def update_summary(self, season):
        """
        Update the summary with data from a season.
        
        Args:
            season: Season object containing application data
        """
        self.season = season
        
        if not season:
            self.eiq_value.setText("0.0")
            self.apps_value.setText("0")
            self.products_value.setText("0")
            self.impact_label.setText("No data")
            self.impact_label.setStyleSheet("padding: 10px; border-radius: 5px; background-color: #F0F0F0;")
            return
        
        # Calculate total EIQ
        total_eiq = season.calculate_season_eiq()
        self.eiq_value.setText(f"{total_eiq:.1f}")
        
        # Count applications
        app_count = len(season.applications)
        self.apps_value.setText(str(app_count))
        
        # Count unique products
        product_names = set()
        for app in season.applications:
            for product in app.products:
                product_names.add(product.name)
        
        product_count = len(product_names)
        self.products_value.setText(str(product_count))
        
        # Set impact rating and color
        if total_eiq < 50:
            impact_text = "Low Environmental Impact"
            impact_color = "#E6F5E6"  # Light green
        elif total_eiq < 100:
            impact_text = "Moderate Environmental Impact"
            impact_color = "#FFF5E6"  # Light yellow
        else:
            impact_text = "High Environmental Impact"
            impact_color = "#F5E6E6"  # Light red
        
        self.impact_label.setText(impact_text)
        self.impact_label.setStyleSheet(f"padding: 10px; border-radius: 5px; background-color: {impact_color};")


class ApplicationListWidget(QWidget):
    """
    Widget displaying a list of applications in a season.
    
    Shows a table of applications with options to add, edit, and delete.
    """
    
    application_selected = Signal(Application)
    add_application_requested = Signal()
    remove_application_requested = Signal(int)
    
    def __init__(self, parent=None):
        """Initialize the application list widget."""
        super().__init__(parent)
        self.parent = parent
        self.applications = []
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Title and add button
        header_layout = QHBoxLayout()
        
        title = QLabel("Applications")
        title.setFont(get_subtitle_font(size=16))
        header_layout.addWidget(title)
        
        add_button = QPushButton("Add Application")
        add_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        add_button.clicked.connect(self.add_application_requested.emit)
        header_layout.addWidget(add_button)
        
        main_layout.addLayout(header_layout)
        
        # Applications table
        self.applications_table = QTableWidget(0, 6)
        self.applications_table.setHorizontalHeaderLabels([
            "Date", "Field", "Method", "Products", "EIQ", "Actions"
        ])
        
        # Set column widths
        header = self.applications_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        # Connect item click
        self.applications_table.cellDoubleClicked.connect(self.application_double_clicked)
        
        main_layout.addWidget(self.applications_table)
    
    def update_applications(self, applications):
        """
        Update the table with applications data.
        
        Args:
            applications: List of Application objects
        """
        self.applications = applications
        self.applications_table.setRowCount(0)
        
        for i, app in enumerate(applications):
            self.applications_table.insertRow(i)
            
            # Date
            date_str = app.date.strftime("%Y-%m-%d")
            self.applications_table.setItem(i, 0, QTableWidgetItem(date_str))
            
            # Field
            self.applications_table.setItem(i, 1, QTableWidgetItem(app.field_name))
            
            # Method
            self.applications_table.setItem(i, 2, QTableWidgetItem(app.application_method))
            
            # Products
            products_str = ", ".join(p.name for p in app.products)
            self.applications_table.setItem(i, 3, QTableWidgetItem(products_str))
            
            # EIQ
            eiq = app.calculate_total_field_eiq()
            eiq_item = QTableWidgetItem(f"{eiq:.1f}")
            
            # Color code EIQ
            if eiq < 20:
                eiq_item.setBackground(QBrush(EIQ_LOW_COLOR))
            elif eiq < 40:
                eiq_item.setBackground(QBrush(EIQ_MEDIUM_COLOR))
            else:
                eiq_item.setBackground(QBrush(EIQ_HIGH_COLOR))
            
            self.applications_table.setItem(i, 4, eiq_item)
            
            # Actions buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 0, 5, 0)
            
            edit_button = QPushButton("Edit")
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #E6F2EA;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #D6EAE0;
                }
            """)
            edit_button.clicked.connect(lambda _, row=i: self.edit_application(row))
            
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #F5E6E6;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #F2D6D6;
                }
            """)
            delete_button.clicked.connect(lambda _, row=i: self.remove_application(row))
            
            actions_layout.addWidget(edit_button)
            actions_layout.addWidget(delete_button)
            
            self.applications_table.setCellWidget(i, 5, actions_widget)
    
    def application_double_clicked(self, row, column):
        """
        Handle double-click on an application row.
        
        Args:
            row: Row index
            column: Column index
        """
        if 0 <= row < len(self.applications):
            self.application_selected.emit(self.applications[row])
    
    def edit_application(self, row):
        """
        Handle edit button click.
        
        Args:
            row: Row index
        """
        if 0 <= row < len(self.applications):
            self.application_selected.emit(self.applications[row])
    
    def remove_application(self, row):
        """
        Handle delete button click.
        
        Args:
            row: Row index
        """
        if 0 <= row < len(self.applications):
            self.remove_application_requested.emit(row)