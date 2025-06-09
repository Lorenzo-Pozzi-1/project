"""
Scenario Comparison Table Widget

A simple widget that displays a single scenario's data in a table format.
Shows applications with their product names and EIQ values.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                              QTableWidgetItem, QHeaderView)
from PySide6.QtCore import Qt
from common import get_medium_font, get_subtitle_font


class ScenarioComparisonTable(QWidget):
    """
    A widget that displays a single scenario as a table.
    
    Shows scenario name, metadata, and applications with EIQ values.
    """
    
    def __init__(self, scenario, parent=None):
        """Initialize the scenario comparison table."""
        super().__init__(parent)
        self.scenario = scenario
        self.setup_ui()
        self.populate_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Scenario title
        self.title_label = QLabel()
        self.title_label.setFont(get_subtitle_font())
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Scenario metadata
        self.metadata_label = QLabel()
        self.metadata_label.setFont(get_medium_font())
        self.metadata_label.setAlignment(Qt.AlignCenter)
        self.metadata_label.setWordWrap(True)
        layout.addWidget(self.metadata_label)
        
        # Applications table
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Application", "EIQ"])
        
        # Basic table configuration
        self.table.setFixedWidth(350)
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.table.setColumnWidth(1, 80)
        self.table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.table)
        
        # Total EIQ label
        self.total_label = QLabel()
        self.total_label.setFont(get_medium_font())
        self.total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.total_label)
    
    def populate_data(self):
        """Populate the widget with scenario data."""
        if not self.scenario:
            return
        
        # Set title
        self.title_label.setText(self.scenario.name or "Unnamed Scenario")
        
        # Set metadata
        metadata_parts = []
        if self.scenario.grower_name:
            metadata_parts.append(f"Grower: {self.scenario.grower_name}")
        if self.scenario.field_name:
            metadata_parts.append(f"Field: {self.scenario.field_name}")
        if self.scenario.field_area and self.scenario.field_area_uom:
            metadata_parts.append(f"Area: {self.scenario.field_area} {self.scenario.field_area_uom}")
        if self.scenario.variety:
            metadata_parts.append(f"Variety: {self.scenario.variety}")
        
        if metadata_parts:
            self.metadata_label.setText(" | ".join(metadata_parts))
        else:
            self.metadata_label.setText("No metadata available")
        
        # Populate applications table
        applications = self.scenario.applications or []
        
        # Filter valid applications
        valid_applications = [app for app in applications 
                            if app.product_name and (app.field_eiq is not None and app.field_eiq > 0)]
        
        if valid_applications:
            # Sort by EIQ descending (highest first)
            sorted_applications = sorted(valid_applications, 
                                       key=lambda app: app.field_eiq or 0, 
                                       reverse=True)
            
            self.table.setRowCount(len(sorted_applications))
            
            total_eiq = 0
            for row, app in enumerate(sorted_applications):
                # Application name
                app_item = QTableWidgetItem(app.product_name)
                app_item.setFlags(app_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, app_item)
                
                # EIQ value
                eiq_value = app.field_eiq or 0
                eiq_item = QTableWidgetItem(f"{eiq_value:.1f}")
                eiq_item.setFlags(eiq_item.flags() & ~Qt.ItemIsEditable)
                eiq_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, 1, eiq_item)
                
                total_eiq += eiq_value
            
            # Set total EIQ
            self.total_label.setText(f"Total EIQ: {total_eiq:.1f}")
            
        else:
            # No valid applications
            self.table.setRowCount(1)
            no_apps_item = QTableWidgetItem("No applications")
            no_apps_item.setFlags(no_apps_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(0, 0, no_apps_item)
            
            eiq_item = QTableWidgetItem("0.0")
            eiq_item.setFlags(eiq_item.flags() & ~Qt.ItemIsEditable)
            eiq_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(0, 1, eiq_item)
            
            self.total_label.setText("Total EIQ: 0.0")
        
        # Resize rows to content
        self.table.resizeRowsToContents()
