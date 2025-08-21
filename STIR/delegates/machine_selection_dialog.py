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
from ..model_machine import Machine
from ..repository_machine import MachineRepository
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
        title_label = QLabel("Select a Machine:")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # Scroll area for machine grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        # Widget to contain the grid
        scroll_widget = QWidget()
        scroll_widget.setStyleSheet("background-color: transparent;")
        grid_layout = QGridLayout(scroll_widget)
        grid_layout.setSpacing(20)
        grid_layout.setContentsMargins(15, 15, 15, 15)
        
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
            
            # Create a card-style button for each machine
            machine_card = QPushButton()
            machine_card.setFixedSize(200, 180)
            machine_card.clicked.connect(lambda checked, name=machine.name: self.select_machine(name))
            
            # Create the card layout
            card_layout = QVBoxLayout(machine_card)
            card_layout.setContentsMargins(10, 10, 10, 10)
            card_layout.setSpacing(8)
            
            # Image container
            image_label = QLabel()
            image_label.setFixedSize(160, 120)
            image_label.setAlignment(Qt.AlignCenter)
            image_label.setStyleSheet("background-color: #ffffff; border-radius: 4px;")
            
            # Load and set the picture
            if machine.picture:
                image_path = resource_path(f"STIR/images/{machine.picture}")
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    # Scale pixmap to fit label while maintaining aspect ratio
                    scaled_pixmap = pixmap.scaled(150, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    image_label.setPixmap(scaled_pixmap)
                else:
                    image_label.setText("No Image\nAvailable")
                    image_label.setStyleSheet("background-color: #ffffff; border-radius: 4px; color: #666; font-size: 10px;")
            else:
                image_label.setText("No Image\nAvailable")
                image_label.setStyleSheet("background-color: #ffffff; border-radius: 4px; color: #666; font-size: 10px;")

            card_layout.addWidget(image_label)
            
            # Machine name label
            name_label = QLabel(machine.name)
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setWordWrap(True)
            name_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #333; background: transparent;")
            card_layout.addWidget(name_label)
            
            # Card styling based on selection state
            if machine.name == self.selected_machine_name:
                machine_card.setStyleSheet("""
                    QPushButton {
                        background-color: #e3f2fd;
                        border: 2px solid #1976d2;
                        border-radius: 8px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #bbdefb;
                        border: 2px solid #1565c0;
                    }
                    QPushButton:pressed {
                        background-color: #90caf9;
                    }
                """)
            else:
                machine_card.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        padding: 0px;
                    }
                    QPushButton:hover {
                        background-color: #f5f5f5;
                        border: 2px solid #1976d2;
                        transform: translateY(-2px);
                    }
                    QPushButton:pressed {
                        background-color: #eeeeee;
                    }
                """)
            
            grid_layout.addWidget(machine_card, row, col)
    
    def select_machine(self, machine_name: str):
        """Handle machine selection and close dialog."""
        self.selected_machine_name = machine_name
        self.machine_selected.emit(machine_name)
        self.accept()
    
    def get_selected_machine(self) -> str:
        """Get the selected machine name."""
        return self.selected_machine_name
