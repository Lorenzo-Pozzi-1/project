"""Applications Table Container for the LORENZO POZZI Pesticide App with drag and drop support."""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, 
                              QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor
from season_planner_page.widgets.application_row import ApplicationRowWidget
from common.styles import COMPARISON_HEADER_STYLE


class ApplicationsTableContainer(QWidget):
    """Container widget for managing multiple application rows with drag and drop support."""
    
    applications_changed = Signal()  # Signal emitted when any application data changes
    
    def __init__(self, parent=None):
        """Initialize the applications table container."""
        super().__init__(parent)
        self.parent = parent
        self.field_area = 10.0  # Default field area
        self.field_area_uom = "ha"  # Default unit of measure
        self.application_rows = []  # List to track application row widgets
        self.dragged_row = None     # Currently dragged row
        self.drop_indicator_index = -1  # Index where drop indicator should be shown
        self.setup_ui()
        
        # Enable drag & drop
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Set up the UI components for the table container."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ----- HEADER SECTION -----
        self._setup_header(main_layout)
        
        # ----- SCROLLABLE CONTENT AREA -----
        self._setup_scroll_area(main_layout)
        
        # ----- DROP INDICATOR -----
        self._create_drop_indicator()
    
    def _setup_header(self, main_layout):
        """Set up the header section of the table."""
        # Create header row
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(5, 5, 5, 5)
        header_layout.setSpacing(5)
        
        # Define headers and their stretch factors
        headers = ["", "App. No", "Date", "Type", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        stretches = [0, 1, 2, 1, 3, 1, 1, 1, 2, 2, 1]
        
        # Create and add header labels
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            if i > 0:  # Skip styling for the drag handle column
                label.setStyleSheet("font-weight: bold;")
            if i == 0:  # Drag handle column
                label.setFixedWidth(20)
            header_layout.addWidget(label)
            header_layout.setStretch(i, stretches[i])
        
        # Create header widget with fixed height
        header_widget = QWidget()
        header_widget.setFixedHeight(ApplicationRowWidget.ROW_HEIGHT)
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet(COMPARISON_HEADER_STYLE)
        
        main_layout.addWidget(header_widget)
    
    def _setup_scroll_area(self, main_layout):
        """Set up the scrollable area for application rows."""
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container widget for rows
        self.rows_container = QWidget()
        self.rows_container.setObjectName("rowsContainer")
        
        # Set styling for container including drop indicator
        self.rows_container.setStyleSheet("""
            QWidget#dropIndicator {
                background-color: #3b82f6;
                height: 3px;
                margin: 0 5px;
            }
        """)
        
        # Create layout for rows
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(5, 5, 5, 5)
        self.rows_layout.setSpacing(1)
        self.rows_layout.addStretch(1)  # Push rows to the top
        
        # Set up the scroll area
        self.scroll_area.setWidget(self.rows_container)
        main_layout.addWidget(self.scroll_area)
    
    def _create_drop_indicator(self):
        """Create the drop indicator for drag and drop operations."""
        self.drop_indicator = QFrame(self.rows_container)
        self.drop_indicator.setObjectName("dropIndicator")
        self.drop_indicator.setFixedHeight(3)
        self.drop_indicator.setVisible(False)
        
    def add_application_row(self):
        """Add a new application row and return the created widget."""
        index = len(self.application_rows)
        row_widget = ApplicationRowWidget(
            parent=self.rows_container, 
            field_area=self.field_area,
            field_area_uom=self.field_area_uom,
            index=index
        )

        # Connect signals
        row_widget.data_changed.connect(self.on_application_data_changed)
        row_widget.drag_started.connect(self.on_row_drag_started)
        row_widget.drag_ended.connect(self.on_row_drag_ended)
        row_widget.delete_requested.connect(self.remove_application_row)
        
        # Add to layout and tracking list
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row_widget)
        self.application_rows.append(row_widget)
        
        # Update all row numbers (or just set this one)
        row_widget.update_app_number(index + 1)

        # Apply alternating row colors
        if index % 2 == 1:  # Odd rows
            palette = row_widget.palette()
            palette.setColor(QPalette.Window, QColor("#F5F7FA"))
            row_widget.setPalette(palette)
            row_widget.setAutoFillBackground(True)

        # Emit signal for the new row
        self.applications_changed.emit()
        return row_widget
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return sum(row.get_field_eiq() for row in self.application_rows)
    
    def get_applications(self):
        """Get all applications as a list of dictionaries, excluding empty ones."""
        applications = []
        for row_widget in self.application_rows:
            app_data = row_widget.get_application_data()
            if app_data:  # Only include rows with a product selected
                applications.append(app_data)
        return applications

    def set_applications(self, applications):
        """Set the container contents from a list of application dictionaries."""
        self.clear_applications()
        
        for app_data in applications:
            row_widget = self.add_application_row()
            row_widget.set_application_data(app_data)

    def clear_applications(self):
        """Clear all application rows from the container."""
        while self.application_rows:
            self.remove_application_row(0)  # Remove first row each time

    def count(self):
        """Get the number of application rows."""
        return len(self.application_rows)

    def on_application_data_changed(self, row_widget):
        """Handle changes to application data in any row."""
        self.applications_changed.emit()

    def on_row_drag_started(self, row_widget):
        """Handle start of row dragging."""
        self.dragged_row = row_widget
        # Store original position
        self.dragged_row_index = row_widget.index
    
    def on_row_drag_ended(self, row_widget):
        """Handle end of row dragging."""
        self.dragged_row = None
        self.drop_indicator.setVisible(False)
        self.drop_indicator_index = -1
        # Renumber indices
        self.update_row_indices()
    
    def update_row_indices(self):
        """Update the indices of all rows after reordering."""
        for i, row in enumerate(self.application_rows):
            row.set_index(i)
            row.update_app_number(i + 1)  # Application numbers are 1-based
    
    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasFormat("application/x-applicationrow-index"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move events to show drop indicator."""
        if not event.mimeData().hasFormat("application/x-applicationrow-index"):
            return
            
        event.acceptProposedAction()
        
        # Calculate drop index based on cursor position
        pos = event.pos()
        drop_y = pos.y()
        
        # Find the index where the row would be dropped
        target_index = -1
        for i, row in enumerate(self.application_rows):
            if row is not self.dragged_row:
                # Get row position
                row_pos = row.pos()
                row_height = row.height()
                row_center = row_pos.y() + row_height / 2
                
                if drop_y < row_center:
                    target_index = i
                    break
        
        # If still -1, drop at the end
        if target_index == -1:
            target_index = len(self.application_rows)
            
        # Don't allow dropping at original position
        if target_index == self.dragged_row_index:
            return
            
        # Update drop indicator
        if target_index != self.drop_indicator_index:
            self.drop_indicator_index = target_index
            self.update_drop_indicator()
    
    def update_drop_indicator(self):
        """Update the position of the drop indicator."""
        if self.drop_indicator_index < 0:
            self.drop_indicator.setVisible(False)
            return
            
        # Position the indicator
        if self.drop_indicator_index < len(self.application_rows):
            # Position at top of the target row
            row = self.application_rows[self.drop_indicator_index]
            pos = row.pos()
            self.drop_indicator.move(5, pos.y() - 1)
        else:
            # Position after the last row
            if self.application_rows:
                last_row = self.application_rows[-1]
                pos = last_row.pos()
                self.drop_indicator.move(5, pos.y() + last_row.height() + 1)
            else:
                # No rows, position at top
                self.drop_indicator.move(5, 5)
        
        # Make visible and size to container width
        self.drop_indicator.setFixedWidth(self.rows_container.width() - 10)
        self.drop_indicator.setVisible(True)
    
    def dropEvent(self, event):
        """Handle drop events to reorder rows."""
        if not event.mimeData().hasFormat("application/x-applicationrow-index"):
            return
            
        # Get source row index
        source_index = int(event.mimeData().data("application/x-applicationrow-index").data().decode())
        target_index = self.drop_indicator_index
        
        # Ensure valid indices
        if target_index < 0 or source_index < 0 or source_index >= len(self.application_rows):
            event.ignore()
            return
            
        # Adjust target index if moving down
        if target_index > source_index:
            target_index -= 1
            
        # Skip if source and target are the same
        if target_index == source_index:
            event.ignore()
            return
            
        # Move the row in the list and layout
        self.move_row(source_index, target_index)
        event.acceptProposedAction()
        
        # Hide drop indicator
        self.drop_indicator.setVisible(False)
        self.drop_indicator_index = -1
    
    def move_row(self, source_index, target_index):
        """
        Move a row from source index to target index with animation.
        
        Args:
            source_index: The index of the row to move
            target_index: The target index to move the row to
        """
        if source_index == target_index:
            return
            
        # Get the widgets
        source_row = self.application_rows[source_index]
        
        # Remove from layout but don't delete
        self.rows_layout.removeWidget(source_row)
        
        # Remove from list and insert at new position
        self.application_rows.pop(source_index)
        self.application_rows.insert(target_index, source_row)
        
        # Insert into layout at new position with animation
        anim_group = QParallelAnimationGroup(self)
        
        # Calculate number of rows to animate
        min_idx = min(source_index, target_index)
        max_idx = max(source_index, target_index)
        
        # Animate all affected rows
        for i, row in enumerate(self.application_rows):
            # Remove from layout first
            self.rows_layout.removeWidget(row)
            
            # Add at current position without animation for rows not affected
            if i < min_idx or i > max_idx:
                self.rows_layout.insertWidget(i, row)
            else:
                # Animate affected rows
                self.rows_layout.insertWidget(i, row)
                
                # Create animation for opacity
                fade_effect = QGraphicsOpacityEffect(row)
                row.setGraphicsEffect(fade_effect)
                fade_effect.setOpacity(0.8)
                
                fade_anim = QPropertyAnimation(fade_effect, b"opacity")
                fade_anim.setDuration(200)
                fade_anim.setStartValue(0.8)
                fade_anim.setEndValue(1.0)
                fade_anim.setEasingCurve(QEasingCurve.OutCubic)
                
                anim_group.addAnimation(fade_anim)
        
        # Update row indices
        self.update_row_indices()
        
        # Start animation
        anim_group.start()
        
        # Emit signal as the order has changed
        self.applications_changed.emit()

    def remove_application_row(self, row=None):
        """
        Remove an application row from the container.
        
        Args:
            row: Row widget, index, or None (to remove last row)
                
        Returns:
            bool: True if a row was removed
        """
        # Determine which row widget to remove
        if isinstance(row, int) and 0 <= row < len(self.application_rows):
            row_widget = self.application_rows[row]
        elif row is None and self.application_rows:
            row_widget = self.application_rows[-1]
        else:
            row_widget = row
        
        # Remove the widget if found
        if row_widget in self.application_rows:
            # Get the index for later use
            index = self.application_rows.index(row_widget)
            
            # Remove from list and layout
            self.application_rows.remove(row_widget)
            self.rows_layout.removeWidget(row_widget)
            row_widget.deleteLater()
            
            # Update indices and app numbers
            self.update_row_indices()
            
            # Emit signal that applications changed
            self.applications_changed.emit()
            return True
        
        return False