"""
Machine Selection Dialog with Pictures.

Provides a visual dialog for selecting machines by their pictures.
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, 
                               QWidget, QPushButton, QLabel, QGridLayout, 
                               QDialogButtonBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QFont
from typing import Optional, List
from ..model_machine import Machine
from ..repository_machine import MachineRepository
from .custom_machine_dialog import CustomMachineDialog
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
        
        # First, create the custom machine card (top-left position)
        self.create_custom_machine_card(grid_layout, 0, 0)
        
        # Then create regular machine cards, starting from position 1
        for i, machine in enumerate(machines):
            # Offset by 1 to account for custom machine card
            position = i + 1
            row = position // columns
            col = position % columns
            
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
                image_path = resource_path(f"STIR/images/machines/{machine.picture}")
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
    
    def create_custom_machine_card(self, grid_layout: QGridLayout, row: int, col: int):
        """Create the custom machine card with plus icon."""
        # Create a card-style button for custom machine
        custom_card = QPushButton()
        custom_card.setFixedSize(200, 180)
        custom_card.clicked.connect(self.open_custom_machine_dialog)
        
        # Create the card layout
        card_layout = QVBoxLayout(custom_card)
        card_layout.setContentsMargins(10, 10, 10, 10)
        card_layout.setSpacing(8)
        
        # Plus icon container
        icon_label = QLabel("+")
        icon_label.setFixedSize(160, 120)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            background-color: #ffffff; 
            border-radius: 4px; 
            font-size: 48px; 
            font-weight: bold; 
            color: #1976d2;
        """)
        card_layout.addWidget(icon_label)
        
        # Custom machine label
        name_label = QLabel("Add Custom Machine")
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setWordWrap(True)
        name_label.setStyleSheet("font-weight: bold; font-size: 11px; color: #333; background: transparent;")
        card_layout.addWidget(name_label)
        
        # Card styling
        custom_card.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px dashed #1976d2;
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
        
        grid_layout.addWidget(custom_card, row, col)
    
    def open_custom_machine_dialog(self):
        """Open the custom machine creation dialog."""
        custom_dialog = CustomMachineDialog(self)
        custom_dialog.machine_created.connect(self.on_custom_machine_created)
        custom_dialog.exec()
    
    def on_custom_machine_created(self, machine: Machine):
        """Handle when a custom machine is created."""
        # For now, just select the new custom machine and close
        # In the future, we might want to refresh the machine list
        self.selected_machine_name = machine.name
        self.machine_selected.emit(machine.name)
        self.accept()
