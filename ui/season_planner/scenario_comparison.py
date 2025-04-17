"""
Scenario Comparison for the Lorenzo Pozzi Pesticide App

This module defines the ScenarioComparison class which allows users
to compare different pesticide application scenarios side by side.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QBrush, QColor

from ui.common.styles import (
    MARGIN_LARGE, SPACING_LARGE, SECONDARY_BUTTON_STYLE, LIGHT_BG_COLOR,
    EIQ_LOW_COLOR, EIQ_MEDIUM_COLOR, EIQ_HIGH_COLOR
)


class ScenarioComparison(QWidget):
    """
    Widget for comparing multiple scenarios side by side.
    """
    def __init__(self, parent=None):
        """Initialize the scenario comparison widget."""
        super().__init__(parent)
        self.parent = parent
        self.scenarios = {}  # Dictionary to store scenario data
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE, MARGIN_LARGE)
        main_layout.setSpacing(SPACING_LARGE)
        
        # Comparison table
        self.comparison_table = QTableWidget()
        self.comparison_table.setColumnCount(3)
        self.comparison_table.setHorizontalHeaderLabels([
            "Number of applications", "EIQ score", "Other info..."
        ])
        
        # Set column widths
        header = self.comparison_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        
        # Style the header
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #007C3E;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        main_layout.addWidget(self.comparison_table)
        
        # Back button
        back_button = QPushButton("< Season planner")
        back_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        back_button.clicked.connect(self.on_back_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(back_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
    
    def update_comparison(self, scenarios):
        """Update the comparison table with scenario data."""
        self.scenarios = scenarios
        self.comparison_table.setRowCount(len(scenarios))
        
        # Populate the table
        for row, (scenario_name, data) in enumerate(scenarios.items()):
            # Scenario name as row header
            self.comparison_table.setVerticalHeaderItem(row, QTableWidgetItem(scenario_name))
            
            # Applications count
            self.comparison_table.setItem(
                row, 0, 
                QTableWidgetItem(str(data.get("num_applications", "N/A")))
            )
            
            # EIQ score
            eiq_item = QTableWidgetItem(str(data.get("eiq_score", "N/A")))
            # Style based on EIQ value
            eiq_score = data.get("eiq_score", 0)
            if eiq_score < 100:
                eiq_item.setBackground(QBrush(EIQ_LOW_COLOR))
            elif eiq_score < 200:
                eiq_item.setBackground(QBrush(EIQ_MEDIUM_COLOR))
            else:
                eiq_item.setBackground(QBrush(EIQ_HIGH_COLOR))
            
            self.comparison_table.setItem(row, 1, eiq_item)
            
            # Other info
            self.comparison_table.setItem(
                row, 2, 
                QTableWidgetItem(data.get("other_info", ""))
            )
        
        # Alternate row colors
        for row in range(self.comparison_table.rowCount()):
            if row % 2 == 1:
                for col in range(self.comparison_table.columnCount()):
                    item = self.comparison_table.item(row, col)
                    if item and not item.background().color().isValid():
                        item.setBackground(QBrush(QColor(LIGHT_BG_COLOR)))
    
    def on_back_clicked(self):
        """Handle back button click."""
        # Signal to parent to switch back to planner view
        if self.parent and hasattr(self.parent, "show_planner_view"):
            self.parent.show_planner_view()