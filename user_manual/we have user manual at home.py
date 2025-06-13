"""
High-fidelity User Manual Dialog using QTextBrowser.

This module recreates the original HTML styling as closely as possible.
"""

import os
from PySide6.QtWidgets import (QDialog, QHBoxLayout, QVBoxLayout, QListWidget, 
                              QListWidgetItem, QFrame, QTextBrowser, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
from common.utils import resource_path

class UserManualDialog(QDialog):
    """High-fidelity QTextBrowser-based user manual dialog."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.content_data = {}
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        """Set up the dialog UI with exact HTML styling."""
        self.setWindowTitle("Pesticides App - User Manual")
        self.setModal(False)
        self.resize(1200, 800)
        self.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        
        # Set dialog background to match HTML
        self.setStyleSheet("QDialog { background-color: #D9D9E4; }")
        
        # Main container widget
        container = QWidget()
        container.setStyleSheet("background-color: #D9D9E4;")
        
        # Main layout
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navigation sidebar - exact match to HTML
        self.setup_sidebar()
        main_layout.addWidget(self.sidebar_frame)
        
        # Content browser with white background
        self.content_browser = QTextBrowser()
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #ffffff;
                border: none;
                padding: 40px;
                font-family: 'Century Gothic', 'Red Hat Display Black', sans-serif;
                font-size: 14px;
                line-height: 24px;
                color: #000000;
            }
        """)
        main_layout.addWidget(self.content_browser)
        
        # Set container as central widget
        dialog_layout = QVBoxLayout(self)
        dialog_layout.setContentsMargins(0, 0, 0, 0)
        dialog_layout.setSpacing(0)
        dialog_layout.addWidget(container)
        
        # McCain yellow footer bar
        footer = QFrame()
        footer.setFixedHeight(20)
        footer.setStyleSheet("background-color: #fee000;")
        dialog_layout.addWidget(footer)
        
    def setup_sidebar(self):
        """Create navigation sidebar with exact HTML styling."""
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(280)
        self.sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #000000;
                color: #ffffff;
                border: none;
            }
        """)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(20, 20, 20, 20)
        sidebar_layout.setSpacing(0)
        
        # Title with exact styling
        title_frame = QFrame()
        title_frame.setFixedHeight(60)
        title_layout = QVBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 30)
        
        title_label = QTextBrowser()
        title_label.setFixedHeight(30)
        title_label.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        title_label.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        title_label.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 0;
                margin: 0;
            }
        """)
        title_label.setHtml("""
            <div style="text-align: center; color: #ffffff; font-size: 18px; font-weight: bold;">
                📖 User Manual<span style="color: #fee000;">.</span>
            </div>
        """)
        title_layout.addWidget(title_label)
        sidebar_layout.addWidget(title_frame)
        
        # Navigation list with exact hover/selection styling
        self.nav_list = QListWidget()
        self.nav_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                font-family: 'Century Gothic', sans-serif;
                font-weight: bold;
                font-size: 14px;
                spacing: 2px;
            }
            QListWidget::item {
                color: #ffffff;
                padding: 8px 12px;
                border-radius: 6px;
                margin-bottom: 4px;
                min-height: 16px;
            }
            QListWidget::item:hover {
                background-color: rgba(201, 191, 176, 0.2);
                color: #C9BFB0;
            }
            QListWidget::item:selected {
                background-color: #C9BFB0;
                color: #434043;
            }
            QListWidget::item:selected:hover {
                background-color: #C9BFB0;
                color: #434043;
            }
        """)
        
        # Add navigation items
        nav_items = [
            ("🏠 Home Page", "home"),
            ("🗃️ Product List & Comparison", "products"),
            ("🧮 EIQ Calculator", "calculator"),
            ("📅 Season Planner", "planner")
        ]
        
        for text, key in nav_items:
            item = QListWidgetItem(text)
            item.setData(Qt.UserRole, key)
            self.nav_list.addItem(item)
        
        self.nav_list.currentItemChanged.connect(self.on_nav_changed)
        sidebar_layout.addWidget(self.nav_list)
        sidebar_layout.addStretch()
        
    def load_content(self):
        """Load HTML content for each section with exact styling."""
        self.content_data = {
            "home": self.get_home_content(),
            "products": self.get_products_content(),
            "calculator": self.get_calculator_content(),
            "planner": self.get_planner_content()
        }
        
        # Set initial content
        self.nav_list.setCurrentRow(0)
        
    def get_base_styles(self):
        """Get exact CSS styles matching the original HTML."""
        return """
        <style>
        body {
            font-family: 'Century Gothic', 'Red Hat Display Black', sans-serif;
            line-height: 1.6;
            color: #000000;
            margin: 0;
            padding: 0;
            background: #ffffff;
        }
        
        h1 {
            color: #000000;
            font-size: 2.2em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #fee000;
            font-weight: bold;
        }
        
        h2 {
            color: #000000;
            font-size: 1.6em;
            margin: 30px 0 15px 0;
            padding-left: 15px;
            border-left: 4px solid #fee000;
            font-weight: bold;
        }
        
        h3 {
            color: #000000;
            font-size: 1.3em;
            margin: 25px 0 12px 0;
            font-weight: bold;
        }
        
        h4 {
            color: #000000;
            margin-bottom: 10px;
            font-size: 1.1em;
            font-weight: bold;
        }
        
        .highlight-box {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #fff3cd, stop:1 #ffeaa7);
            border-left: 4px solid #fee000;
            padding: 20px;
            margin: 20px 0;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .highlight-box strong {
            color: #ec3400;
            font-weight: bold;
        }
        
        .feature-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            margin: 10px 0;
            transition: transform 0.3s ease;
        }
        
        .feature-card h4 {
            color: #000000;
            margin-bottom: 10px;
            font-size: 1.1em;
            font-weight: bold;
        }
        
        .image-placeholder {
            background: #D9D9E4;
            border: 2px dashed #434043;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            border-radius: 8px;
            color: #7f8c8d;
            font-style: italic;
            min-height: 120px;
        }
        
        .step-number {
            display: inline-block;
            background: #fee000;
            color: #000000;
            width: 25px;
            height: 25px;
            border-radius: 50%;
            text-align: center;
            line-height: 25px;
            margin-right: 10px;
            font-weight: bold;
            vertical-align: middle;
        }
        
        ul, ol {
            padding-left: 30px;
            margin: 15px 0;
        }
        
        li {
            margin-bottom: 8px;
            line-height: 1.6;
        }
        
        li strong {
            font-weight: bold;
            color: #000000;
        }
        
        p {
            margin: 15px 0;
            line-height: 1.6;
        }
        
        .warning {
            background: #fee;
            border: 1px solid #f5c6cb;
            color: #ec3400;
            padding: 15px;
            border-radius: 6px;
            margin: 20px 0;
        }
        
        /* McCain yellow accent */
        .mccain-yellow {
            color: #fee000;
        }
        </style>
        """
        
    def get_home_content(self):
        """Get home page content with exact HTML styling."""
        return f"""
        {self.get_base_styles()}
        <body>
        <h1>🏠 Home Page<span class="mccain-yellow">.</span></h1>
        
        <div class="highlight-box">
            <strong>Note:</strong> Depending on your screen size, the aspect may differ slightly, but all the elements remain the same.
        </div>
        
        <div class="image-placeholder">
            [Home Page Screenshot - Would show actual image here]
        </div>
        
        <div class="feature-card">
            <h4>🌍 Preferences Row</h4>
            <p>Set your preferences, they will be maintained between sessions and will be used to provide you the correct information for your region, and to calculate the doses of pesticides applied as seed treatments or as amount/length of row.</p>
        </div>
        
        <div class="feature-card">
            <h4>🧭 Navigation Buttons</h4>
            <p>Use them to navigate to the main features!</p>
        </div>
        
        <div class="feature-card">
            <h4>📊 EIQ Info Material</h4>
            <p>A concise explanation of EIQ scores, and a link to Cornell's website to find out more about them.</p>
        </div>
        
        <div class="feature-card">
            <h4>📖 Help button</h4>
            <p>Open the user manual, but I guess you already figured this out :)</p>
        </div>
        
        <div class="feature-card">
            <h4>🔗 Give Feedback or Report Problems</h4>
            <p>Access the forms to give feedback or report problems that you might encounter.</p>
        </div>
        </body>
        """
        
    def get_products_content(self):
        """Get products page content with exact HTML styling."""
        return f"""
        {self.get_base_styles()}
        <body>
        <h1>🗃️ Products List and Comparison<span class="mccain-yellow">.</span></h1>
        
        <div class="highlight-box">
            <strong>Note:</strong> Depending on your screen size, the aspect may differ slightly, but all the elements remain the same.
        </div>
        
        <h2>Products List Tab</h2>
        
        <div class="image-placeholder">
            [Products List Tab Screenshot - Would show actual image here]
        </div>
        
        <p>The Products List provides a view of all pesticides approved by McCain available in your region. Key features include:</p>
        
        <ul>
            <li><strong>Filters:</strong> Filter products by any attribute, up to four filters</li>
            <li><strong>Sortable columns:</strong> Click any column header to sort data</li>
            <li><strong>Selectable rows:</strong> Check a product's box to select it, you can view the fact sheet of this one product or select more for comparison</li>
            <li><strong>Compare/View button:</strong> Click it to switch view to the Products Comparison tab, or to view the fact sheet of the selected product</li>
            <li><strong>Reset button:</strong> Reset all filters and sorting to default, go back to the products list tab if you're in the comparison view</li>
        </ul>
        
        <h2>Products Comparison Tab</h2>
        
        <div class="image-placeholder">
            [Products Comparison Tab Screenshot - Would show actual image here]
        </div>
        
        <p>View quick fact sheets, with more detailed information, for the selected product(s). Compare multiple products side-by-side to make informed decisions.</p>
        </body>
        """
        
    def get_calculator_content(self):
        """Get calculator page content with exact HTML styling."""
        return f"""
        {self.get_base_styles()}
        <body>
        <h1>🧮 EIQ Calculator<span class="mccain-yellow">.</span></h1>
        
        <div class="highlight-box">
            <strong>Note:</strong> Depending on your screen size, the aspect may differ slightly, but all the elements remain the same.
        </div>
        
        <h2>Single Product Calculator (CORRECT TEXT!)</h2>
        
        <div class="image-placeholder">
            [Single Calculator Screenshot - Would show actual image here]
        </div>
        
        <p>Calculate detailed Environmental Impact Quotients for individual applications:</p>
        
        <ol>
            <li><strong>Product Selection:</strong> Choose a pesticide from the filtered dropdown menu</li>
            <li><strong>Application Rate:</strong> Enter your planned application rate</li>
            <li><strong>Application Area:</strong> Specify the treatment area</li>
            <li><strong>Results Analysis:</strong> Review calculated Field Use EIQ and impact breakdown</li>
        </ol>
        
        <h3>Understanding EIQ Results</h3>
        <p>The calculator provides three key risk categories:</p>
        
        <ul>
            <li><strong>Farm Worker Risk:</strong> Potential exposure risks for applicators and field workers</li>
            <li><strong>Consumer Risk:</strong> Food safety considerations for end consumers</li>
            <li><strong>Ecological Risk:</strong> Environmental impact on beneficial organisms and ecosystems</li>
        </ul>
        
        <h2>Multiple Products Calculator</h2>
        
        <div class="image-placeholder">
            [Multi Calculator Screenshot - Would show actual image here]
        </div>
        
        <p>Compare EIQ values across multiple products with simplified interface for quick comparisons. This tool is ideal for:</p>
        
        <ul>
            <li>Rapid comparison of treatment alternatives</li>
            <li>Identifying lower-impact options</li>
            <li>Supporting sustainable pest management decisions</li>
        </ul>
        
        <div class="highlight-box">
            <strong>Remember:</strong> Field Use EIQ = Active Ingredient EIQ × AI Concentration × Application Rate. Higher scores indicate greater environmental impact.
        </div>
        </body>
        """
        
    def get_planner_content(self):
        """Get planner page content with exact HTML styling."""
        return f"""
        {self.get_base_styles()}
        <body>
        <h1>📅 Season Planner<span class="mccain-yellow">.</span></h1>
        
        <div class="highlight-box">
            <strong>Note:</strong> Depending on your screen size, the aspect may differ slightly, but all the elements remain the same.
        </div>
        
        <div class="image-placeholder">
            [Season Planner Screenshots - Would show actual images here]
        </div>
        
        <h2>Creating Treatment Scenarios</h2>
        <p>The Season Planner allows you to create comprehensive treatment plans for entire growing seasons:</p>
        
        <h3><span class="step-number">1</span>Scenario Management</h3>
        <ul>
            <li>Create new scenarios for different fields or treatment strategies</li>
            <li>Load and modify existing scenarios from previous seasons</li>
            <li>Save scenarios with descriptive names for easy identification</li>
        </ul>
        
        <h3><span class="step-number">2</span>Adding Applications</h3>
        <ol>
            <li>Click "Add Row" to add a new pesticide application</li>
            <li>Select the product from the dropdown menu</li>
            <li>Enter application rate and timing</li>
            <li>Specify target area and application method</li>
        </ol>
        
        <h3><span class="step-number">3</span>EIQ Analysis</h3>
        <p>View cumulative environmental impact across all planned applications:</p>
        <ul>
            <li>Total seasonal EIQ scores</li>
            <li>Individual application contributions</li>
            <li>Risk category breakdowns</li>
        </ul>
        
        <h2>Importing Scenarios</h2>
        
        <div class="image-placeholder">
            [Import Scenario Screenshots - Would show actual images here]
        </div>
        
        <p>Import scenarios from previous years or external sources:</p>
        
        <ol>
            <li>Navigate to the import function</li>
            <li>Select your source file or scenario</li>
            <li>Review and modify imported data as needed</li>
            <li>Save the imported scenario with a new name</li>
        </ol>
        </body>
        """
        
    def on_nav_changed(self, current, previous):
        """Handle navigation changes."""
        if current:
            section_key = current.data(Qt.UserRole)
            if section_key in self.content_data:
                self.content_browser.setHtml(self.content_data[section_key])


def create_user_manual_dialog(main_window):
    """Create and return a user manual dialog for the main window."""
    return UserManualDialog(main_window)