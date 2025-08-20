"""
Machine Selection Dialog with Pictures.

Provides a visual dialog for selecting machines by their pictures.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, 
                               QWidget, QPushButton, QLabel, QGridLayout, 
                               QDialogButtonBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from typing import Optional, List
from .model_machine import Machine
from .repository_machine import MachineRepository
from common.utils import resource_path


class MachineSelectionDialog(QDialog):
    """Dialog for selecting machines using visual pictures."""
    
    machine_selected = Signal(str)  # Emits the selected machine name
    
    def __init__(self, parent=None, current_machine_name: str = ""):
        super().__init__(parent)
        self.selected_machine_name = current_machine_name
        self.machine_repo = MachineRepository.get_instance()
        
        self.setWindowTitle("Select Machine")
        self.setModal(True)
        self.resize(800, 600)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog user interface."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Select a Machine by clicking on its picture:")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Scroll area for machine grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget to contain the grid
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        grid_layout.setSpacing(15)
        
        # Load machines and create picture buttons
        machines = self.machine_repo.get_all_machines()
        self.create_machine_buttons(grid_layout, machines)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Cancel)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def create_machine_buttons(self, grid_layout: QGridLayout, machines: List[Machine]):
        """Create clickable picture buttons for each machine."""
        columns = 3  # Number of columns in the grid
        
        for i, machine in enumerate(machines):
            row = i // columns
            col = i % columns
            
            # Create a frame for each machine
            machine_frame = QFrame()
            machine_frame.setFrameStyle(QFrame.Box)
            machine_frame.setLineWidth(2)
            
            # Highlight if this is the currently selected machine
            if machine.name == self.selected_machine_name:
                machine_frame.setStyleSheet("QFrame { border: 3px solid #007ACC; }")
            else:
                machine_frame.setStyleSheet("QFrame { border: 1px solid #ccc; }")
            
            frame_layout = QVBoxLayout(machine_frame)
            frame_layout.setContentsMargins(10, 10, 10, 10)
            
            # Machine picture button
            picture_button = QPushButton()
            picture_button.setFixedSize(180, 140)
            picture_button.clicked.connect(lambda checked, name=machine.name: self.select_machine(name))
            
            # Load and set the picture
            if machine.picture:
                image_path = resource_path(f"STIR/images/{machine.picture}")
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale pixmap to fit button while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(170, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    picture_button.setIcon(scaled_pixmap)
                    picture_button.setIconSize(scaled_pixmap.size())
                else:
                    picture_button.setText("No Image")
            else:
                picture_button.setText("No Image")
            
            picture_button.setStyleSheet("""
                QPushButton {
                    border: 1px solid #ccc;
                    background-color: white;
                }
                QPushButton:hover {
                    border: 2px solid #007ACC;
                    background-color: #f0f8ff;
                }
                QPushButton:pressed {
                    background-color: #e0e8ff;
                }
            """)
            
            frame_layout.addWidget(picture_button)
            
            # Machine name label
            name_label = QLabel(machine.name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setStyleSheet("font-weight: bold; margin-top: 5px;")
            frame_layout.addWidget(name_label)
            
            grid_layout.addWidget(machine_frame, row, col)
    
    def select_machine(self, machine_name: str):
        """Handle machine selection and close dialog."""
        self.selected_machine_name = machine_name
        self.machine_selected.emit(machine_name)
        self.accept()
    
    def get_selected_machine(self) -> str:
        """Get the selected machine name."""
        return self.selected_machine_name
