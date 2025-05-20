"""Applications Table Container for the LORENZO POZZI Pesticide App with drag and drop support."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, Signal, QEasingCurve, QParallelAnimationGroup, QPropertyAnimation
from PySide6.QtGui import QPalette, QColor
from common import ContentFrame, BLUE_LINE_DROP_STYLE, GENERIC_TABLE_STYLE, WHITE, ALTERNATE_ROW_COLOR
from season_planner_page.widgets.application_row import ApplicationRowWidget


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
        self.dragged_row_index = -1  # Index of dragged row
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
        
        # Wrap header in ContentFrame
        header_frame = ContentFrame()
        header_layout = QVBoxLayout()
        
        # Header row
        header_row_layout = QHBoxLayout()
        header_row_layout.setContentsMargins(2, 1, 2, 1)
        header_row_layout.setSpacing(5)
        
        # Define headers and their stretch factors
        headers = ["", "App. No", "Date", "Type", "Product", "Rate", "UOM", "Area", "Method", "AI Groups", "Field EIQ"]
        stretches = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
        
        # Create and add header labels
        for i, header_text in enumerate(headers):
            label = QLabel(header_text)
            label.setAlignment(Qt.AlignCenter)
            if i > 0:  # Skip styling for the drag handle column
                label.setStyleSheet("font-weight: bold;")
            if i == 0:  # Drag handle column
                label.setFixedWidth(20)
            header_row_layout.addWidget(label)
            header_row_layout.setStretch(i, stretches[i])
        
        # Extra column for delete button
        header_row_layout.addWidget(QLabel(""))
        header_row_layout.setStretch(len(headers), 0)
        
        header_layout.addLayout(header_row_layout)
        header_frame.layout.addLayout(header_layout)
        
        # Apply the comparison header style
        header_frame.setStyleSheet(GENERIC_TABLE_STYLE)
        header_frame.setFixedHeight(ApplicationRowWidget.ROW_HEIGHT)
        
        main_layout.addWidget(header_frame)
        
        # Wrap scroll area in ContentFrame
        content_frame = ContentFrame()
        content_layout = QVBoxLayout()
        
        # Create scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create container for rows
        self.rows_container = QWidget()
        self.rows_container.setObjectName("rowsContainer")
        self.rows_container.setStyleSheet(BLUE_LINE_DROP_STYLE)
        
        # Create layout for rows
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(5, 5, 5, 5)
        self.rows_layout.setSpacing(1)
        self.rows_layout.addStretch(1)  # Push rows to the top
        
        # Set up the scroll area
        self.scroll_area.setWidget(self.rows_container)
        content_layout.addWidget(self.scroll_area)
        
        content_frame.layout.addLayout(content_layout)
        main_layout.addWidget(content_frame)
        
        # Create drop indicator
        self.drop_indicator = QFrame(self.rows_container)
        self.drop_indicator.setObjectName("dropIndicator")
        self.drop_indicator.setFixedHeight(3)
        self.drop_indicator.setVisible(False)
        self.drop_indicator.raise_()  # Ensure it's on top of other widgets
    
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
        
        # Update row number
        row_widget.update_app_number(index + 1)

        # Update row colors after adding new row
        self.update_row_colors()

        # Emit signal for the new row
        self.applications_changed.emit()
        return row_widget
    
    def update_row_colors(self):
        """Apply alternating background colors to all rows."""
        for i, row in enumerate(self.application_rows):
            palette = row.palette()
            if i % 2 == 1:  # Odd rows
                palette.setColor(QPalette.Window, QColor(ALTERNATE_ROW_COLOR))
            else:  # Even rows
                palette.setColor(QPalette.Window, QColor(WHITE))
            row.setPalette(palette)
            row.setAutoFillBackground(True)
    
    def get_total_field_eiq(self):
        """Calculate the total Field EIQ for all applications."""
        return sum(row.get_field_eiq() for row in self.application_rows)
    
    def get_applications(self):
        """Get all applications as a list of dictionaries, excluding empty ones."""
        return [app_data for row_widget in self.application_rows 
                if (app_data := row_widget.get_application_data())]

    def set_applications(self, applications):
        """Set the container contents from a list of application dictionaries."""
        self.clear_applications()
        
        for app_data in applications:
            row_widget = self.add_application_row()
            row_widget.set_application_data(app_data)
        
        # Make sure colors are correctly applied after loading applications
        self.update_row_colors()

    def clear_applications(self):
        """Clear all application rows from the container."""
        while self.application_rows:
            self.remove_application_row(self.application_rows[0])

    def set_field_area(self, area, uom):
        """Set the default field area for new applications."""
        self.field_area = area
        self.field_area_uom = uom

    def on_application_data_changed(self, row_widget):
        """Handle changes to application data in any row."""
        self.applications_changed.emit()

    def on_row_drag_started(self, row_widget):
        """Handle start of row dragging."""
        self.dragged_row = row_widget
        self.dragged_row_index = row_widget.index
    
    def on_row_drag_ended(self, row_widget):
        """Handle end of row dragging."""
        self.dragged_row = None
        self.drop_indicator.setVisible(False)
        self.drop_indicator_index = -1
        self.update_row_indices()
    
    def update_row_indices(self):
        """Update the indices of all rows after reordering."""
        for i, row in enumerate(self.application_rows):
            row.set_index(i)
            row.update_app_number(i + 1)
        
        # Update row colors whenever indices are updated
        self.update_row_colors()

    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasFormat("application/x-applicationrow-index"):
            event.acceptProposedAction()
    
    def dragMoveEvent(self, event):
        """Handle drag move events to show drop indicator."""
        if not event.mimeData().hasFormat("application/x-applicationrow-index"):
            return
            
        event.acceptProposedAction()
        
        # Find drop position
        drop_y = event.pos().y()
        target_index = len(self.application_rows)
        
        for i, row in enumerate(self.application_rows):
            if row is not self.dragged_row:
                row_pos = row.pos()
                row_center = row_pos.y() + row.height() / 2
                
                if drop_y < row_center:
                    target_index = i
                    break
        
        # Don't allow dropping at original position
        if target_index == self.dragged_row_index:
            return
            
        # Update drop indicator if position changed
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
            self.drop_indicator.move(5, row.pos().y() - 1)
        else:
            # Position after the last row
            if self.application_rows:
                last_row = self.application_rows[-1]
                self.drop_indicator.move(5, last_row.pos().y() + last_row.height() + 1)
            else:
                # No rows, position at top
                self.drop_indicator.move(5, 5)
        
        # Size and show
        self.drop_indicator.setFixedWidth(self.rows_container.width() - 10)
        self.drop_indicator.setVisible(True)
        
        # Ensure it's on top
        self.drop_indicator.raise_()
    
    def dropEvent(self, event):
        """Handle drop events to reorder rows."""
        if not event.mimeData().hasFormat("application/x-applicationrow-index"):
            return
            
        # Get source and target indices
        source_index = int(event.mimeData().data("application/x-applicationrow-index").data().decode())
        target_index = self.drop_indicator_index
        
        # Validate indices
        if target_index < 0 or source_index < 0 or source_index >= len(self.application_rows):
            event.ignore()
            return
            
        # Adjust target index if moving down
        if target_index > source_index:
            target_index -= 1
            
        # Skip if same position
        if target_index == source_index:
            event.ignore()
            return
            
        # Move the row
        self.move_row(source_index, target_index)
        event.acceptProposedAction()
        
        # Hide drop indicator
        self.drop_indicator.setVisible(False)
        self.drop_indicator_index = -1
    
    def move_row(self, source_index, target_index):
        """Move a row from source index to target index with animation."""
        if source_index == target_index:
            return
            
        # Get the source row
        source_row = self.application_rows[source_index]
        
        # Remove from list and layout
        self.rows_layout.removeWidget(source_row)
        self.application_rows.pop(source_index)
        
        # Insert at new position
        self.application_rows.insert(target_index, source_row)
        
        # Create animation group
        anim_group = QParallelAnimationGroup(self)
        
        # Determine affected range
        min_idx = min(source_index, target_index)
        max_idx = max(source_index, target_index)
        
        # Reinsert all rows with animation for affected range
        for i, row in enumerate(self.application_rows):
            self.rows_layout.removeWidget(row)
            self.rows_layout.insertWidget(i, row)
            
            # Animate affected rows
            if min_idx <= i <= max_idx:
                fade_effect = QGraphicsOpacityEffect(row)
                row.setGraphicsEffect(fade_effect)
                fade_effect.setOpacity(0.8)
                
                fade_anim = QPropertyAnimation(fade_effect, b"opacity")
                fade_anim.setDuration(200)
                fade_anim.setStartValue(0.8)
                fade_anim.setEndValue(1.0)
                fade_anim.setEasingCurve(QEasingCurve.OutCubic)
                
                anim_group.addAnimation(fade_anim)
        
        # Update indices and start animation
        self.update_row_indices()
        anim_group.start()
        self.applications_changed.emit()

    def remove_application_row(self, row):
        """Remove an application row from the container."""
        if row not in self.application_rows:
            return False
            
        # Remove from list and layout
        self.application_rows.remove(row)
        self.rows_layout.removeWidget(row)
        row.deleteLater()
        
        # Update indices
        self.update_row_indices()
        self.applications_changed.emit()
        return True
    
    def update_default_field_area(self, area, uom):
        """
        Update the default field area for new applications without changing existing rows.
        """
        self.field_area = area
        self.field_area_uom = uom