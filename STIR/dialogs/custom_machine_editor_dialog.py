"""
New Custom Machine Creation Dialog with tabbed tool interface.

Provides a dialog for creating custom machines with multiple tools,
each managed in its own tab.
"""

import csv
import os
import shutil
import tempfile
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QLineEdit, QDoubleSpinBox, QPushButton,
                               QDialogButtonBox, QLabel, QMessageBox, QSpinBox,
                               QFileDialog, QSlider, QCheckBox, QComboBox, QPlainTextEdit,
                               QTextEdit, QTabWidget, QWidget, QScrollArea, QFrame, QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from typing import List, Tuple
from ..data.model_custom_machine import CustomMachine, CustomMachineTool
from ..data.repository_custom_machine import CustomMachineRepository
from common.utils import resource_path


class ToolTabWidget(QWidget):
    """Widget for editing a single tool's properties."""
    
    def __init__(self, tool: CustomMachineTool = None, parent=None):
        super().__init__(parent)
        self.tool = tool if tool else CustomMachineTool()
        self.setup_ui()
        if tool:
            self.populate_fields()
    
    def setup_ui(self):
        """Set up the tool editing interface."""
        layout = QVBoxLayout(self)
        
        # Create a scroll area in case we need more space
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main widget inside scroll area
        main_widget = QWidget()
        form_layout = QFormLayout(main_widget)
        
        # Tool name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter tool name (e.g., Primary Disc, Chisel)")
        form_layout.addRow("Tool Name:*", self.name_edit)
        
        # PTO operated checkbox
        self.rotates_checkbox = QCheckBox("Tool is PTO operated")
        form_layout.addRow("PTO Operated:", self.rotates_checkbox)
        
        # Working depth with unit selection
        depth_layout = QHBoxLayout()
        self.depth_spinbox = QDoubleSpinBox()
        self.depth_spinbox.setRange(0.1, 1000.0)
        self.depth_spinbox.setValue(6.0)
        self.depth_spinbox.setDecimals(1)
        depth_layout.addWidget(self.depth_spinbox)
        
        self.depth_uom_combo = QComboBox()
        self.depth_uom_combo.addItems(["in", "cm"])
        self.depth_uom_combo.setCurrentText("in")
        depth_layout.addWidget(self.depth_uom_combo)
        
        form_layout.addRow("Working Depth:*", depth_layout)
        
        # Surface area disturbed
        self.surface_area_spinbox = QSpinBox()
        self.surface_area_spinbox.setRange(1, 100)
        self.surface_area_spinbox.setValue(100)
        self.surface_area_spinbox.setSuffix(" %")
        form_layout.addRow("Surface Area Disturbed:*", self.surface_area_spinbox)
        
        # Tillage factor with help button
        tillage_layout = QHBoxLayout()
        self.tillage_spinbox = QDoubleSpinBox()
        self.tillage_spinbox.setRange(0.01, 1.0)
        self.tillage_spinbox.setValue(0.70)
        self.tillage_spinbox.setSingleStep(0.05)
        self.tillage_spinbox.setDecimals(2)
        tillage_layout.addWidget(self.tillage_spinbox)
        
        # Help button
        help_button = QPushButton("?")
        help_button.setFixedSize(20, 20)
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
        """)
        help_button.clicked.connect(self.show_tillage_factor_help)
        tillage_layout.addWidget(help_button)
        
        form_layout.addRow("Tillage Factor:*", tillage_layout)
                
        # Note about mandatory fields
        note_label = QLabel("* Required fields")
        note_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        form_layout.addRow(note_label)
        
        scroll.setWidget(main_widget)
        layout.addWidget(scroll)
    
    def populate_fields(self):
        """Populate fields with tool data."""
        self.name_edit.setText(self.tool.name)
        self.rotates_checkbox.setChecked(self.tool.rotates)
        self.depth_spinbox.setValue(self.tool.depth)
        self.depth_uom_combo.setCurrentText(self.tool.depth_uom)
        self.surface_area_spinbox.setValue(int(self.tool.surface_area_disturbed))
        self.tillage_spinbox.setValue(self.tool.tillage_type_factor)
    
    def get_tool_data(self) -> CustomMachineTool:
        """Get tool data from the form."""
        return CustomMachineTool(
            name=self.name_edit.text().strip(),
            rotates=self.rotates_checkbox.isChecked(),
            depth=self.depth_spinbox.value(),
            depth_uom=self.depth_uom_combo.currentText(),
            surface_area_disturbed=float(self.surface_area_spinbox.value()),
            tillage_type_factor=self.tillage_spinbox.value()
        )
    
    def validate(self) -> Tuple[bool, str]:
        """Validate the tool data."""
        if not self.name_edit.text().strip():
            return False, "Tool name is required"
        
        if self.depth_spinbox.value() <= 0:
            return False, "Working depth must be greater than 0"
        
        if self.surface_area_spinbox.value() <= 0:
            return False, "Surface area disturbed must be greater than 0"
        
        if self.tillage_spinbox.value() <= 0:
            return False, "Tillage factor must be greater than 0"
        
        return True, ""
    
    def show_tillage_factor_help(self):
        """Show help dialog for tillage factor selection."""
        help_text = """
        <h3>Tillage Factor Guidelines</h3>
        <p>Select the appropriate tillage factor based on the tool's operation:</p>
        <ul>
        <li><b>1.0:</b> Inversion + mixing (moldboard plow, disk plow)</li>
        <li><b>0.8:</b> Mixing + some inversion (disk harrow, rotary hoe)</li>
        <li><b>0.7:</b> Mixing only (field cultivator, chisel plow)</li>
        <li><b>0.4:</b> Lifting + fracturing (subsoiler, deep ripper)</li>
        <li><b>0.15:</b> Compression (roller, cultipacker)</li>
        </ul>
        <p>Choose the factor that best matches your tool's soil disturbance pattern.</p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Tillage Factor Help")
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec()


class NewCustomMachineDialog(QDialog):
    """Dialog for creating or editing custom machines with tabbed tool interface."""
    
    machine_created = Signal(CustomMachine)
    
    def __init__(self, parent=None, machine_to_edit: CustomMachine = None):
        super().__init__(parent)
        self.machine_to_edit = machine_to_edit
        self.is_editing = machine_to_edit is not None
        self.picture_cleared = False
        self.tool_tabs = []  # List to store tool tab widgets
        
        title = "Edit Custom Machine" if self.is_editing else "Create Custom Machine"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(700, 600)
        
        self.setup_ui()
        
        # Pre-populate fields if editing
        if self.is_editing:
            self.populate_edit_fields()
        else:
            # Add one default tool tab for new machines
            self.add_tool_tab()
    
    def setup_ui(self):
        """Set up the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_text = "Edit Custom Machine" if self.is_editing else "Create Custom Machine"
        title_label = QLabel(title_text)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 5px 0px;")
        layout.addWidget(title_label)
        
        # Machine basic info section
        machine_frame = QFrame()
        machine_frame.setFrameStyle(QFrame.StyledPanel)
        machine_layout = QFormLayout(machine_frame)
        
        # Machine name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter custom machine name")
        machine_layout.addRow("Machine Name:*", self.name_edit)
        
        # Operating speed with unit selection
        speed_layout = QHBoxLayout()
        self.speed_spinbox = QDoubleSpinBox()
        self.speed_spinbox.setRange(0.1, 100.0)
        self.speed_spinbox.setValue(5.0)
        self.speed_spinbox.setDecimals(1)
        speed_layout.addWidget(self.speed_spinbox)
        
        self.speed_uom_combo = QComboBox()
        self.speed_uom_combo.addItems(["mph", "km/h"])
        self.speed_uom_combo.setCurrentText("mph")
        speed_layout.addWidget(self.speed_uom_combo)
        
        machine_layout.addRow("Operating Speed:*", speed_layout)
        
        # Picture selection
        picture_layout = QHBoxLayout()
        self.picture_path = ""
        self.picture_label = QLabel("No picture selected")
        self.picture_label.setStyleSheet("color: #666; font-style: italic;")
        picture_layout.addWidget(self.picture_label)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_picture)
        picture_layout.addWidget(self.browse_button)
        
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_picture)
        picture_layout.addWidget(self.clear_button)
        
        machine_layout.addRow("Picture:", picture_layout)
        
        # Notes field
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter notes or description for this custom machine...")
        self.notes_edit.setMaximumHeight(80)  # Limit height
        machine_layout.addRow("Notes:", self.notes_edit)
        
        layout.addWidget(machine_frame)
        
        # Tools section
        tools_label = QLabel("Tools Configuration")
        tools_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0px 5px 0px;")
        layout.addWidget(tools_label)
        
        # Tool management buttons
        tool_buttons_layout = QHBoxLayout()
        self.add_tool_button = QPushButton("Add Tool")
        self.add_tool_button.clicked.connect(self.add_tool_tab)
        tool_buttons_layout.addWidget(self.add_tool_button)
        
        tool_buttons_layout.addStretch()
        layout.addLayout(tool_buttons_layout)
        
        # Tools tab widget
        self.tools_tab_widget = QTabWidget()
        self.tools_tab_widget.setTabsClosable(True)
        self.tools_tab_widget.setMovable(True)
        self.tools_tab_widget.tabCloseRequested.connect(self.remove_tool_tab)
        layout.addWidget(self.tools_tab_widget)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Update remove button state
        self.update_tool_buttons()
    
    def add_tool_tab(self, tool: CustomMachineTool = None):
        """Add a new tool tab."""
        if len(self.tool_tabs) >= 10:
            QMessageBox.warning(self, "Maximum Tools", "You can only add up to 10 tools per machine.")
            return
        
        tool_widget = ToolTabWidget(tool)
        self.tool_tabs.append(tool_widget)
        
        tab_name = f"Tool {len(self.tool_tabs)}"
        if tool and tool.name:
            tab_name = tool.name[:15] + "..." if len(tool.name) > 15 else tool.name
        
        self.tools_tab_widget.addTab(tool_widget, tab_name)
        self.tools_tab_widget.setCurrentWidget(tool_widget)
        self.update_tool_buttons()
    
    def remove_tool_tab(self, index: int):
        """Remove a tool tab at the specified index."""
        if 0 <= index < len(self.tool_tabs):
            # Get tool name for confirmation dialog
            tool_widget = self.tool_tabs[index]
            tool_data = tool_widget.get_tool_data()
            tool_name = tool_data.name if tool_data.name else f"Tool {index + 1}"
            
            # Show confirmation dialog
            reply = QMessageBox.question(
                self,
                "Remove Tool",
                f"Are you sure you want to remove '{tool_name}'?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.tools_tab_widget.removeTab(index)
                self.tool_tabs.pop(index)
                self.update_tab_names()
                self.update_tool_buttons()
    
    def update_tab_names(self):
        """Update tab names after removal."""
        for i, tool_widget in enumerate(self.tool_tabs):
            tool_data = tool_widget.get_tool_data()
            tab_name = f"Tool {i + 1}"
            if tool_data.name:
                tab_name = tool_data.name[:15] + "..." if len(tool_data.name) > 15 else tool_data.name
            self.tools_tab_widget.setTabText(i, tab_name)
    
    def update_tool_buttons(self):
        """Update the state of tool management buttons."""
        self.add_tool_button.setEnabled(len(self.tool_tabs) < 10)
    
    def populate_edit_fields(self):
        """Populate fields when editing an existing machine."""
        self.name_edit.setText(self.machine_to_edit.name)
        self.speed_spinbox.setValue(self.machine_to_edit.speed)
        self.speed_uom_combo.setCurrentText(self.machine_to_edit.speed_uom)
        self.notes_edit.setPlainText(self.machine_to_edit.notes)
        
        if self.machine_to_edit.picture:
            self.picture_path = self.machine_to_edit.picture
            self.picture_label.setText(self.machine_to_edit.picture)
            self.picture_label.setStyleSheet("color: black;")
        
        # Add tool tabs
        for tool in self.machine_to_edit.tools:
            self.add_tool_tab(tool)
    
    def browse_picture(self):
        """Browse for a picture file."""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Image files (*.png *.jpg *.jpeg *.gif *.bmp)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                # Get just the filename
                filename = os.path.basename(file_path)
                self.picture_path = file_path
                self.picture_label.setText(filename)
                self.picture_label.setStyleSheet("color: black;")
                self.picture_cleared = False
    
    def clear_picture(self):
        """Clear the selected picture."""
        self.picture_path = ""
        self.picture_label.setText("No picture selected")
        self.picture_label.setStyleSheet("color: #666; font-style: italic;")
        self.picture_cleared = True
    
    def validate_machine(self) -> Tuple[bool, str]:
        """Validate the machine data."""
        # Check machine name
        if not self.name_edit.text().strip():
            return False, "Machine name is required"
        
        # Check speed
        if self.speed_spinbox.value() <= 0:
            return False, "Operating speed must be greater than 0"
        
        # Check that at least one tool is configured
        if len(self.tool_tabs) == 0:
            return False, "At least one tool must be configured"
        
        # Validate all tools
        for i, tool_widget in enumerate(self.tool_tabs):
            is_valid, error_msg = tool_widget.validate()
            if not is_valid:
                return False, f"Tool {i + 1}: {error_msg}"
        
        return True, ""
    
    def accept_dialog(self):
        """Handle dialog acceptance."""
        # Validate input
        is_valid, error_msg = self.validate_machine()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        try:
            # Create machine object
            tools = [tool_widget.get_tool_data() for tool_widget in self.tool_tabs]
            
            machine = CustomMachine(
                name=self.name_edit.text().strip(),
                speed=self.speed_spinbox.value(),
                speed_uom=self.speed_uom_combo.currentText(),
                picture=self.get_picture_filename(),
                notes=self.notes_edit.toPlainText().strip(),
                tools=tools
            )
            
            # Copy picture if needed
            if self.picture_path and os.path.exists(self.picture_path):
                self.copy_picture_to_images_folder()
            
            # Save to repository
            repository = CustomMachineRepository.get_instance()
            if self.is_editing:
                success = repository.update_machine(self.machine_to_edit.name, machine)
                if not success:
                    QMessageBox.critical(self, "Error", "Failed to update machine in repository")
                    return
            else:
                success = repository.add_machine(machine)
                if not success:
                    QMessageBox.critical(self, "Error", "Failed to add machine to repository")
                    return
            
            # Emit signal and close
            self.machine_created.emit(machine)
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while saving the machine: {str(e)}")
    
    def get_picture_filename(self) -> str:
        """Get the picture filename to store."""
        if self.picture_cleared or not self.picture_path:
            return ""
        
        if os.path.exists(self.picture_path):
            return os.path.basename(self.picture_path)
        
        # If editing and original picture exists
        if self.is_editing and self.machine_to_edit.picture:
            return self.machine_to_edit.picture
        
        return ""
    
    def copy_picture_to_images_folder(self):
        """Copy selected picture to the custom machines images folder."""
        if not self.picture_path or not os.path.exists(self.picture_path):
            return
        
        try:
            images_dir = resource_path("STIR/data/images/custom_machines")
            os.makedirs(images_dir, exist_ok=True)
            
            filename = os.path.basename(self.picture_path)
            dest_path = os.path.join(images_dir, filename)
            
            if self.picture_path != dest_path:
                shutil.copy2(self.picture_path, dest_path)
                
        except Exception as e:
            print(f"Error copying picture: {e}")
