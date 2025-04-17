"""
Scenario Editor for the Lorenzo Pozzi Pesticide App

This module defines the ScenarioEditor class which allows users
to create and edit pesticide application scenarios.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QLineEdit, QHeaderView, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor

from ui.common.styles import (
    get_subtitle_font, SPACING_MEDIUM, LIGHT_BG_COLOR
)

from ui.season_planner.models import Scenario, Treatment


class ScenarioEditor(QWidget):
    """
    Widget for editing a single scenario with treatments and EIQ info.
    """
    def __init__(self, scenario_name, parent=None):
        """Initialize a scenario editor widget."""
        super().__init__(parent)
        self.parent = parent
        self.scenario = Scenario(scenario_name)
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components for the scenario editor."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING_MEDIUM)
        
        # Metadata section
        metadata_frame = QFrame()
        metadata_frame.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 4px;")
        metadata_layout = QHBoxLayout(metadata_frame)
        
        # Metadata fields
        grower_label = QLabel("Grower:")
        self.grower_input = QLineEdit()
        self.grower_input.textChanged.connect(self.update_grower)
        
        field_label = QLabel("Field:")
        self.field_input = QLineEdit()
        self.field_input.textChanged.connect(self.update_field)
        
        variety_label = QLabel("Variety:")
        self.variety_input = QLineEdit()
        self.variety_input.textChanged.connect(self.update_variety)
        
        # Add metadata fields to layout
        metadata_layout.addWidget(grower_label)
        metadata_layout.addWidget(self.grower_input)
        metadata_layout.addWidget(field_label)
        metadata_layout.addWidget(self.field_input)
        metadata_layout.addWidget(variety_label)
        metadata_layout.addWidget(self.variety_input)
        
        # View more info button
        info_button = QPushButton("View more info")
        info_button.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #007C3E;
                border: 1px solid #007C3E;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #E6F2EA;
            }
        """)
        metadata_layout.addWidget(info_button)
        
        main_layout.addWidget(metadata_frame)
        
        # EIQ Score section
        eiq_frame = QFrame()
        eiq_frame.setMaximumHeight(150)
        eiq_layout = QVBoxLayout(eiq_frame)
        
        # EIQ title
        eiq_title = QLabel("EIQ score")
        eiq_title.setAlignment(Qt.AlignCenter)
        eiq_title.setFont(get_subtitle_font(16))
        eiq_layout.addWidget(eiq_title)
        
        # EIQ Score value
        self.eiq_value_label = QLabel("0")
        self.eiq_value_label.setAlignment(Qt.AlignCenter)
        self.eiq_value_label.setFont(get_subtitle_font(20))
        eiq_layout.addWidget(self.eiq_value_label)
        
        # EIQ description
        eiq_desc = QLabel("Total Environmental Impact Quotient")
        eiq_desc.setAlignment(Qt.AlignCenter)
        eiq_layout.addWidget(eiq_desc)
        
        main_layout.addWidget(eiq_frame)
        
        # Treatments table - initialize it first
        self.init_treatments_table()
        # Then add it to the layout - this way the table exists but isn't trying to update EIQ yet
        main_layout.addWidget(self.treatments_table)
    
    def init_treatments_table(self):
        """Initialize the treatments table."""
        self.treatments_table = QTableWidget()
        self.treatments_table.setColumnCount(1)  # Start with one column
        self.treatments_table.setHorizontalHeaderLabels(["Treatment N."])
        
        # Define rows
        treatment_rows = [
            "Product 1 type", "Product 1 name", "Active ingredient group",
            "Product 2 type", "Product 2 name", "Active ingredient group",
            "Product 3 type", "Product 3 name", "Active ingredient group",
            "...",
            "Field EIQ / ha"
        ]
        
        self.treatments_table.setRowCount(len(treatment_rows))
        
        # Set the row headers
        for i, row_label in enumerate(treatment_rows):
            item = QTableWidgetItem(row_label)
            if "Field EIQ" in row_label:
                item.setBackground(QBrush(QColor("#e6f2ea")))  # Light green background
            self.treatments_table.setVerticalHeaderItem(i, item)
        
        # Set up table appearance
        self.treatments_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.treatments_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.treatments_table.verticalHeader().setDefaultAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Make the vertical header section wider
        self.treatments_table.verticalHeader().setMinimumWidth(150)
        
        # Connect cell change signal
        self.treatments_table.itemChanged.connect(self.handle_cell_changed)
        
        # Add an "Add treatment" column with button
        add_treatment_widget = QWidget()
        add_treatment_layout = QVBoxLayout(add_treatment_widget)
        
        # Add spacer at the top to push the button down
        add_treatment_layout.addSpacerItem(QSpacerItem(10, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Add treatment button
        add_treatment_button = QPushButton("+\nAdd treatment")
        add_treatment_button.setMinimumSize(80, 80)
        add_treatment_button.setStyleSheet("""
            QPushButton {
                background-color: #e6f2ea;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d6eae0;
            }
        """)
        add_treatment_button.clicked.connect(self.add_treatment)
        add_treatment_layout.addWidget(add_treatment_button)
        
        # Add spacer at the bottom
        add_treatment_layout.addSpacerItem(QSpacerItem(10, 80, QSizePolicy.Minimum, QSizePolicy.Expanding))
        add_treatment_layout.setContentsMargins(5, 0, 5, 0)
    
    def add_treatment(self):
        """Add a new treatment column to the table and data model."""
        # Add to data model first
        treatment = self.scenario.add_treatment()
        
        # Now update the UI
        current_cols = self.treatments_table.columnCount()
        
        # Add a new column
        self.treatments_table.insertColumn(current_cols)
        
        # Set the header for the new column
        new_header_item = QTableWidgetItem(str(current_cols + 1))
        self.treatments_table.setHorizontalHeaderItem(current_cols, new_header_item)
        
        # Only update EIQ display if the label exists
        if hasattr(self, 'eiq_value_label'):
            self.update_eiq_display()
    
    def handle_cell_changed(self, item):
        """Handle changes to table cells."""
        row = item.row()
        col = item.column()
        value = item.text()
        
        # Make sure we have enough treatments in the model
        while col >= len(self.scenario.treatments):
            self.scenario.add_treatment()
        
        treatment = self.scenario.treatments[col]
        
        # Handle different row types
        if row == 0:  # Product 1 type
            if len(treatment.products) == 0:
                treatment.add_product('', '', '')
            treatment.products[0]['type'] = value
        elif row == 1:  # Product 1 name
            if len(treatment.products) == 0:
                treatment.add_product('', '', '')
            treatment.products[0]['name'] = value
        elif row == 2:  # Product 1 AI group
            if len(treatment.products) == 0:
                treatment.add_product('', '', '')
            treatment.products[0]['active_ingredient_group'] = value
        elif row == 3:  # Product 2 type
            if len(treatment.products) <= 1:
                treatment.add_product('', '', '')
            treatment.products[1]['type'] = value
        elif row == 4:  # Product 2 name
            if len(treatment.products) <= 1:
                treatment.add_product('', '', '')
            treatment.products[1]['name'] = value
        elif row == 5:  # Product 2 AI group
            if len(treatment.products) <= 1:
                treatment.add_product('', '', '')
            treatment.products[1]['active_ingredient_group'] = value
        elif row == 6:  # Product 3 type
            if len(treatment.products) <= 2:
                treatment.add_product('', '', '')
            treatment.products[2]['type'] = value
        elif row == 7:  # Product 3 name
            if len(treatment.products) <= 2:
                treatment.add_product('', '', '')
            treatment.products[2]['name'] = value
        elif row == 8:  # Product 3 AI group
            if len(treatment.products) <= 2:
                treatment.add_product('', '', '')
            treatment.products[2]['active_ingredient_group'] = value
        elif "Field EIQ" in self.treatments_table.verticalHeaderItem(row).text():
            treatment.set_field_eiq(value)
            self.update_eiq_display()
    
    def update_eiq_display(self):
        """Update the EIQ score display."""
        total_eiq = self.scenario.get_total_eiq()
        self.eiq_value_label.setText(str(int(total_eiq)))
    
    def update_grower(self, text):
        """Update the grower in the scenario model."""
        self.scenario.grower = text
    
    def update_field(self, text):
        """Update the field in the scenario model."""
        self.scenario.field = text
    
    def update_variety(self, text):
        """Update the variety in the scenario model."""
        self.scenario.variety = text
    
    def get_data_for_comparison(self):
        """Get scenario data for comparison view."""
        return self.scenario.get_data_for_comparison()