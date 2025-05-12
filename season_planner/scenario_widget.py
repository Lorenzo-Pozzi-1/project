"""
Scenario widget for the Season Planner.

This module provides a widget that contains field info and treatments 
for a single scenario.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QTableWidgetItem
from PySide6.QtCore import Qt, Signal
from common.widgets import ScoreBar
from common.styles import get_subtitle_font
from season_planner.models import Treatment, Scenario
from season_planner.field_info_widget import FieldInfoWidget
from season_planner.treatment_table import TreatmentTable

class ScenarioWidget(QWidget):
    """Widget for a single scenario in the Season Planner."""
    
    scenario_changed = Signal()  # Signal when the scenario data changes
    
    def __init__(self, scenario=None, parent=None):
        super().__init__(parent)
        self.scenario = scenario or Scenario()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Field information widget
        self.field_info = FieldInfoWidget()
        self.field_info.info_changed.connect(self._on_field_info_changed)
        layout.addWidget(self.field_info)
        
        # Treatment table
        self.treatment_table = TreatmentTable()
        self.treatment_table.treatment_changed.connect(self._on_treatment_changed)
        self.treatment_table.treatment_deleted.connect(self._on_treatment_deleted)
        self.treatment_table.add_treatment_clicked.connect(self._on_add_treatment)
        layout.addWidget(self.treatment_table)
        
        # Add the "+ add treatment" row
        self.treatment_table.add_treatment_row()
        
        # Create summary section
        summary_frame = QFrame()
        summary_frame.setFrameShape(QFrame.NoFrame)
        summary_layout = QVBoxLayout(summary_frame)
        
        # EIQ summary label
        self.eiq_label = QLabel("Season field EIQ score: 0.0")
        self.eiq_label.setFont(get_subtitle_font())
        self.eiq_label.setAlignment(Qt.AlignCenter)
        summary_layout.addWidget(self.eiq_label)
        
        # EIQ score bar
        self.score_bar = ScoreBar()
        self.score_bar.set_value(0, "Low")
        summary_layout.addWidget(self.score_bar)
        
        layout.addWidget(summary_frame)
        
        # Update UI with initial data if available
        self.update_from_scenario()
    
    def update_from_scenario(self):
        """Update the UI from the scenario data."""
        # Update field info
        self.field_info.set_field_info(
            self.scenario.grower,
            self.scenario.field,
            self.scenario.variety
        )
        
        # Clear existing treatments (except the add row)
        while self.treatment_table.rowCount() > 0:
            self.treatment_table.removeRow(0)
        
        # Add treatments from scenario
        for treatment in self.scenario.treatments:
            row = self.treatment_table.add_empty_row()
            self.treatment_table.setItem(row, 1, QTableWidgetItem(treatment.date))
            self.treatment_table.setItem(row, 2, QTableWidgetItem(treatment.product_name))
            self.treatment_table.setItem(row, 3, QTableWidgetItem(str(treatment.rate)))
            self.treatment_table.setItem(row, 4, QTableWidgetItem(treatment.rate_uom))
            self.treatment_table.setItem(row, 5, QTableWidgetItem(str(treatment.acres)))
            self.treatment_table.setItem(row, 6, QTableWidgetItem(treatment.application_method))
            self.treatment_table.setItem(row, 7, QTableWidgetItem(treatment.active_groups))
            self.treatment_table.update_field_eiq(row, treatment.field_eiq)
        
        # Add the "+ add treatment" row back
        self.treatment_table.add_treatment_row()
        
        # Update summary
        self.update_summary()
    
    def update_summary(self):
        """Update the EIQ summary information."""
        total_eiq = self.scenario.total_field_eiq
        self.eiq_label.setText(f"Season field EIQ score: {total_eiq:.1f}")
        self.score_bar.set_value(total_eiq, self._get_eiq_category(total_eiq))
    
    def _get_eiq_category(self, eiq_value):
        """Get the EIQ category based on value."""
        if eiq_value < 33.3:
            return "Low"
        elif eiq_value < 66.6:
            return "Medium"
        else:
            return "High"
    
    def _on_field_info_changed(self):
        """Handle changes to field information."""
        info = self.field_info.get_field_info()
        self.scenario.grower = info["grower"]
        self.scenario.field = info["field"]
        self.scenario.variety = info["variety"]
        self.scenario_changed.emit()
    
    def _on_treatment_changed(self):
        """Handle changes to treatments."""
        # Update the scenario with data from the table
        self._update_scenario_from_table()
        
        # Update the summary
        self.update_summary()
        
        # Emit the changed signal
        self.scenario_changed.emit()
    
    def _on_treatment_deleted(self, row_index):
        """Handle deletion of a treatment."""
        # Remove from data model
        self.scenario.remove_treatment(row_index)
        self.update_summary()
        self.scenario_changed.emit()
    
    def _on_add_treatment(self):
        """Handle adding a new treatment."""
        # Update from the table first to ensure all changes are captured
        self._update_scenario_from_table()
        
        # Add empty treatment to the scenario
        self.scenario.add_treatment(Treatment())
        
        # Update the table - remove add row first
        self.treatment_table.removeRow(self.treatment_table.rowCount() - 1)
        
        # Add empty row
        new_row = self.treatment_table.add_empty_row()
        
        # Add back the add treatment row
        self.treatment_table.add_treatment_row()
        
        # Emit change signal
        self.scenario_changed.emit()

    def _update_scenario_from_table(self):
        """Update the scenario data model from the table."""
        # Clear existing treatments
        self.scenario.treatments = []
        
        # Skip the last row (add treatment row)
        for row in range(self.treatment_table.rowCount() - 1):
            # Extract data from the table
            date_item = self.treatment_table.item(row, 1)
            product_item = self.treatment_table.item(row, 2)
            rate_item = self.treatment_table.item(row, 3)
            uom_item = self.treatment_table.item(row, 4)
            acres_item = self.treatment_table.item(row, 5)
            method_item = self.treatment_table.item(row, 6)
            groups_item = self.treatment_table.item(row, 7)
            eiq_item = self.treatment_table.item(row, 8)
            
            # Extract values (handle None cases)
            date = date_item.text() if date_item else ""
            product_name = product_item.text() if product_item else ""
            rate = float(rate_item.text()) if rate_item and rate_item.text() else 0.0
            rate_uom = uom_item.text() if uom_item else ""
            acres = float(acres_item.text()) if acres_item and acres_item.text() else 0.0
            method = method_item.text() if method_item else ""
            groups = groups_item.text() if groups_item else ""
            field_eiq = float(eiq_item.text()) if eiq_item and eiq_item.text() else 0.0
            
            # Create treatment object
            treatment = Treatment(
                date=date,
                product=product_name,  # Just store the name for now
                rate=rate,
                rate_uom=rate_uom,
                acres=acres,
                application_method=method,
                field_eiq=field_eiq
            )
            treatment.active_groups = groups
            
            # Add to scenario
            self.scenario.treatments.append(treatment)

    def clear_scenario(self):
        """Clear all data in the scenario."""
        # Clear field info
        self.field_info.set_field_info("", "", "")
        
        # Clear treatments
        self.scenario.treatments = []
        
        # Update UI
        self.update_from_scenario()
        
        # Emit change signal
        self.scenario_changed.emit()