"""
Products list tab for the Lorenzo Pozzi Pesticide App

This module defines the ProductsListTab class which handles the product listing
and filtering functionality with Qt's Model/View architecture.
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
                               QTableView, QHeaderView, QCheckBox, QComboBox, QLineEdit, 
                               QFrame, QScrollArea, QSizePolicy, QStyledItemDelegate,
                               QAbstractItemView, QStyleOptionButton, QStyle, QApplication)
from PySide6.QtCore import Qt, Signal, QItemSelectionModel, QPoint, QRect, QSize
from PySide6.QtGui import QColor, QBrush
from common.styles import get_body_font, PRIMARY_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from data.product_repository import ProductRepository
from data.models import ProductTableModel, ProductFilterProxyModel


class FilterRow(QWidget):
    """
    A filter row widget containing field selection and filter input.
    
    This widget provides a single filter criteria consisting of a field
    dropdown and a text input for the filter value.
    """
    
    filter_changed = Signal(int, str)  # Signal emitted when the filter changes (column, text)
    remove_requested = Signal(object)  # Signal emitted when remove button is clicked
    
    def __init__(self, column_headers, parent=None):
        """
        Initialize a filter row with the given column headers.
        
        Args:
            column_headers: List of column header names
        """
        super().__init__(parent)
        self.column_headers = column_headers
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components with simplified structure."""
        # Single horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Field selection dropdown
        self.field_combo = QComboBox()
        self.field_combo.addItem("Select field...")
        self.field_combo.addItems(self.column_headers)
        self.field_combo.setMinimumWidth(150)
        self.field_combo.currentIndexChanged.connect(self.on_filter_changed)
        layout.addWidget(self.field_combo)
        
        # Contains label
        contains_label = QLabel("contains:")
        layout.addWidget(contains_label)
        
        # Filter value input
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Type to filter...")
        self.value_input.textChanged.connect(self.on_filter_changed)
        layout.addWidget(self.value_input)
        
        # Remove button
        self.remove_button = QPushButton("×")  # Using × character for close icon
        self.remove_button.setFixedSize(24, 24)
        self.remove_button.setToolTip("Remove this filter")
        self.remove_button.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        self.remove_button.clicked.connect(self.request_remove)
        layout.addWidget(self.remove_button)
    
    def on_filter_changed(self):
        """Handle changes to the filter criteria."""
        column_idx = self.field_combo.currentIndex() - 1  # -1 to account for "Select field..."
        filter_text = self.value_input.text().strip()
        
        # Only emit for valid column selections
        if column_idx >= 0:
            self.filter_changed.emit(column_idx, filter_text)
    
    def request_remove(self):
        """Request removal of this filter row."""
        self.remove_requested.emit(self)
    
    def clear(self):
        """Clear filter selections."""
        self.field_combo.setCurrentIndex(0)
        self.value_input.clear()


class SelectionDelegate(QStyledItemDelegate):
    """
    Delegate to handle selection checkboxes in the first column.
    """
    
    selection_changed = Signal(int, bool)  # (row, checked)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checked_rows = set()
    
    def paint(self, painter, option, index):
        """Paint the checkbox."""
        # Use the default painting for non-checkbox columns
        if index.column() != 0:
            return super().paint(painter, option, index)
            
        # Draw checkbox directly, don't use QWidget.render
        checked = index.row() in self._checked_rows
        
        # Save painter state
        painter.save()
        
        # Get the checkbox style option
        style = QApplication.style()
        checkboxOption = QStyleOptionButton()
        checkboxOption.rect = option.rect
        checkboxOption.state = QStyle.State_Enabled
        
        if checked:
            checkboxOption.state |= QStyle.State_On
        else:
            checkboxOption.state |= QStyle.State_Off
            
        # Center the checkbox in the cell
        checkBoxRect = style.subElementRect(QStyle.SE_CheckBoxIndicator, checkboxOption)
        point = QPoint(
            option.rect.x() + option.rect.width() // 2 - checkBoxRect.width() // 2,
            option.rect.y() + option.rect.height() // 2 - checkBoxRect.height() // 2
        )
        checkboxOption.rect = QRect(point, checkBoxRect.size())
        
        # Draw the checkbox
        style.drawControl(QStyle.CE_CheckBox, checkboxOption, painter)
        
        # Restore painter state
        painter.restore()
    
    def editorEvent(self, event, model, option, index):
        """Handle mouse clicks on checkboxes."""
        if index.column() != 0:
            return False
            
        # Only handle mouse press events
        if event.type() == event.Type.MouseButtonRelease:
            # Get the row
            row = index.row()
            
            # Toggle check state
            if row in self._checked_rows:
                self._checked_rows.remove(row)
                checked = False
            else:
                self._checked_rows.add(row)
                checked = True
                
            # Emit signal
            self.selection_changed.emit(row, checked)
            
            # Signal data change to trigger repaint
            model.dataChanged.emit(index, index)
            return True
            
        return False
    
    def sizeHint(self, option, index):
        """Return the size hint for the checkbox."""
        if index.column() != 0:
            return super().sizeHint(option, index)
            
        # Return a size appropriate for a checkbox
        style = QApplication.style()
        checkboxOption = QStyleOptionButton()
        checkboxSize = style.sizeFromContents(
            QStyle.CT_CheckBox, 
            checkboxOption, 
            QSize()
        )
        return checkboxSize
    
    def setChecked(self, row, checked):
        """Set the checked state of a row."""
        if checked:
            self._checked_rows.add(row)
        elif row in self._checked_rows:
            self._checked_rows.remove(row)
    
    def clearChecked(self):
        """Clear all checked rows."""
        self._checked_rows.clear()


class ProductsListTab(QWidget):
    """
    Products list tab for displaying and filtering the products.
    
    This tab displays a table of products with advanced filtering capabilities
    using Qt's Model/View architecture.
    """
    def __init__(self, parent=None):
        """Initialize the products list tab."""
        super().__init__(parent)
        self.parent = parent
        self.filter_rows = []  # Track filter row widgets
        self.setup_ui()
        self.load_product_data()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)
        
        # Set up the filter section
        self.setup_filter_section(main_layout)
        
        # Create table view for products
        self.products_table = QTableView()
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setSortingEnabled(True)
        
        # Set up the custom selection delegate
        self.selection_delegate = SelectionDelegate(self.products_table)
        self.selection_delegate.selection_changed.connect(self.on_product_selection_changed)
        self.products_table.setItemDelegateForColumn(0, self.selection_delegate)
        
        # Set size policy for table to expand and fill available space
        self.products_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Create the table model
        self.product_model = ProductTableModel(parent=self)
        
        # Create the filter proxy model
        self.filter_proxy_model = ProductFilterProxyModel(parent=self)
        self.filter_proxy_model.setSourceModel(self.product_model)
        
        # Set the model for the table view
        self.products_table.setModel(self.filter_proxy_model)
        
        # Add table to main layout with stretch factor 1 (gets all remaining space)
        main_layout.addWidget(self.products_table, 1)
        
        # "Compare Selected" button
        compare_button = QPushButton("View Fact Sheet / Compare Selected Products")
        compare_button.setStyleSheet(PRIMARY_BUTTON_STYLE)
        compare_button.clicked.connect(self.parent.compare_selected_products)
        compare_button.setMinimumWidth(300)
        compare_button.setFont(get_body_font())
        
        main_layout.addWidget(compare_button, alignment=Qt.AlignRight)
    
    def setup_filter_section(self, main_layout):
        """Set up the filter section with simplified layout."""
        # Filter container
        filter_container = QWidget()
        filter_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)
        
        # Filter title
        filter_title = QLabel("Filter Products")
        filter_title.setFont(get_body_font(bold=True))
        filter_layout.addWidget(filter_title)
        
        # Horizontal scrollable area for filter rows
        self.filter_rows_container = QWidget()
        self.filter_rows_layout = QHBoxLayout(self.filter_rows_container)
        self.filter_rows_layout.setContentsMargins(0, 0, 0, 0)
        self.filter_rows_layout.setSpacing(10)
        self.filter_rows_layout.setAlignment(Qt.AlignLeft)
        
        # Add the scrollable area
        filter_scroll = QScrollArea()
        filter_scroll.setWidgetResizable(True)
        filter_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        filter_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        filter_scroll.setFrameShape(QFrame.NoFrame)
        filter_scroll.setWidget(self.filter_rows_container)
        filter_scroll.setMaximumHeight(60)  # Reduced height for horizontal filters
        filter_layout.addWidget(filter_scroll)
        
        # Add Filter button
        add_filter_button = QPushButton("Add Another Filter")
        add_filter_button.setStyleSheet(SECONDARY_BUTTON_STYLE)
        add_filter_button.clicked.connect(self.add_filter_row)
        filter_layout.addWidget(add_filter_button, alignment=Qt.AlignLeft)
        
        # Add to main layout
        main_layout.addWidget(filter_container, 0)
    
    def load_product_data(self):
        """Load product data from the repository."""
        # Load products from repository
        repo = ProductRepository.get_instance()
        products = repo.get_filtered_products()
        
        # Update the model with new products
        self.product_model.setProducts(products)
        
        # Configure the table view columns
        self.configure_table_columns()
        
        # Initialize filters now that we have columns
        self.clear_filter_rows()
        self.add_filter_row()
        
        # Clear selection state when loading new data
        self.selection_delegate.clearChecked()
        
        # Inform parent of empty selection
        if hasattr(self.parent, 'selected_products'):
            self.parent.selected_products = []
    
    def configure_table_columns(self):
        """Configure the table columns for optimal display."""
        # Configure header resize modes
        header = self.products_table.horizontalHeader()
        
        # Adjust size of selection column
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.products_table.setColumnWidth(0, 40)
        
        # Set other columns to resize by content or stretch
        for col in range(1, self.product_model.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.Stretch)
        
        # Columns that should resize to content
        content_resize_cols = ["Min Rate", "Max Rate", "Rate UOM", "REI (h)", "PHI (d)", "Min Days Between"]
        
        # Find column indexes for these headers
        for col in range(1, self.product_model.columnCount()):
            header_text = self.product_model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            if header_text in content_resize_cols:
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)
    
    def add_filter_row(self):
        """Add a new filter row to the filter section."""
        # Get column headers from the model for the filter dropdown
        headers = []
        for col in range(1, self.product_model.columnCount()):  # Skip column 0 (checkbox)
            header = self.product_model.headerData(col, Qt.Horizontal, Qt.DisplayRole)
            headers.append(header)
        
        # Create a new filter row
        filter_row = FilterRow(headers, self)
        filter_row.filter_changed.connect(self.on_filter_criteria_changed)
        filter_row.remove_requested.connect(self.remove_filter_row)
        
        # Add to layout
        self.filter_rows_layout.addWidget(filter_row)
        
        # Add to tracking list
        self.filter_rows.append(filter_row)
        
        # Hide remove button on first row if it's the only one
        if len(self.filter_rows) == 1:
            filter_row.remove_button.setVisible(False)
        else:
            # Make sure all remove buttons are visible if we have multiple rows
            for row in self.filter_rows:
                row.remove_button.setVisible(True)
    
    def remove_filter_row(self, filter_row):
        """Remove a filter row from the filter section."""
        if filter_row in self.filter_rows:
            # Get the column index of this filter
            column_idx = filter_row.field_combo.currentIndex() - 1  # -1 for "Select field..."
            
            # Clear filter in proxy model if column is valid
            if column_idx >= 0:
                self.filter_proxy_model.setFilterCriteria(column_idx, "")
            
            # Remove from layout
            self.filter_rows_layout.removeWidget(filter_row)
            
            # Remove from tracking list
            self.filter_rows.remove(filter_row)
            
            # Delete the widget
            filter_row.deleteLater()
            
            # Hide remove button on first row if it's the only one
            if len(self.filter_rows) == 1:
                self.filter_rows[0].remove_button.setVisible(False)
    
    def clear_filter_rows(self):
        """Clear all filter rows."""
        # Clear all active filters in the proxy model
        self.filter_proxy_model.clearFilters()
        
        # Remove all filter rows
        for filter_row in self.filter_rows:
            self.filter_rows_layout.removeWidget(filter_row)
            filter_row.deleteLater()
        
        # Clear tracking list
        self.filter_rows = []
    
    def on_filter_criteria_changed(self, column, filter_text):
        """Handle changes to a filter criteria."""
        # Apply filter to the proxy model 
        # (column + 1 to skip the selection column in the view)
        self.filter_proxy_model.setFilterCriteria(column + 1, filter_text)
    
    def on_product_selection_changed(self, row, checked):
        """Handle product selection changes."""
        # Convert row from proxy model to source model
        source_row = self.filter_proxy_model.mapToSource(
            self.filter_proxy_model.index(row, 0)).row()
        
        # Get the product from the model
        product = self.product_model.getProduct(source_row)
        
        if product:
            if checked:
                if hasattr(self.parent, 'selected_products') and product not in self.parent.selected_products:
                    self.parent.selected_products.append(product)
            else:
                if hasattr(self.parent, 'selected_products') and product in self.parent.selected_products:
                    self.parent.selected_products.remove(product)
    
    def refresh_product_data(self):
        """Refresh product data when filters have changed."""
        self.load_product_data()