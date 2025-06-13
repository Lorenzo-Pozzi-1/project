# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the current directory (where main.py is located)
project_root = os.path.dirname(os.path.abspath('main.py'))

# Define data files to include
data_files = [
    # Config file
    ('config.json', '.'),
    
    # Data CSV files
    ('data/csv_AI.csv', 'data'),
    ('data/csv_products.csv', 'data'),
    ('data/csv_UOM.csv', 'data'),
    
    # Help files (include all files in help directory)
    ('help/*', 'help'),
]

# Hidden imports - modules that PyInstaller might miss
hidden_imports = [
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    
    # Your application modules
    'common',
    'common.constants',
    'common.styles',
    'common.utils',
    'common.calculations',
    'common.widgets',
    'common.widgets.header_frame_buttons',
    'common.widgets.product_selection',
    'common.widgets.application_params',
    'common.widgets.scorebar',
    'common.widgets.UOM_selector',
    
    'data',
    'data.model_AI',
    'data.model_application',
    'data.model_product',
    'data.model_scenario',
    'data.repository_AI',
    'data.repository_product',
    'data.repository_UOM',
    
    'main_page',
    'main_page.window_main',
    'main_page.page_home',
    'main_page.widget_preferences_row',
    
    'products_page',
    'products_page.page_products',
    'products_page.tab_products_list',
    'products_page.tab_products_comparison',
    'products_page.widget_filter_row',
    'products_page.widget_products_table',
    'products_page.widget_comparison_table',
    
    'eiq_calculator_page',
    'eiq_calculator_page.page_eiq_calculator',
    'eiq_calculator_page.tab_single_calculator',
    'eiq_calculator_page.tab_multi_calculator',
    'eiq_calculator_page.widget_product_card',
    'eiq_calculator_page.widgets_results_display',
    
    'season_planner_page',
    'season_planner_page.page_scenarios_manager',
    'season_planner_page.page_sceanrios_comparison',
    'season_planner_page.tab_scenario',
    'season_planner_page.widgets',
    'season_planner_page.widgets.metadata_widget',
    'season_planner_page.widgets.applications_table',
    'season_planner_page.widgets.eiq_summary',
    'season_planner_page.widgets.scenario_comparison_table',
    'season_planner_page.models',
    'season_planner_page.models.application_table_model',
    'season_planner_page.models.application_validator',
    'season_planner_page.models.application_eiq_calculator',
    'season_planner_page.delegates',
    'season_planner_page.delegates.date_delegate',
    'season_planner_page.delegates.numeric_delegate',
    'season_planner_page.delegates.method_delegate',
    'season_planner_page.delegates.product_name_delegate',
    'season_planner_page.delegates.uom_delegate',
    'season_planner_page.delegates.product_type_delegate',
    'season_planner_page.delegates.reorder_delegate',
    'season_planner_page.import_export',
    'season_planner_page.import_export.excel_parser',
    'season_planner_page.import_export.import_dialog',
    'season_planner_page.import_export.exporter',
    
    'help',
    'help.user_manual_dialog',
        
    # Standard library modules that might be needed
    'pandas',
    'openpyxl',
    'requests',
    'urllib3',
    'json',
    'datetime',
    'typing',
    'dataclasses',
    'collections',
    'traceback',
]

# Exclude PySide5 and other unwanted modules
excludes = [
    'PySide5',
    'PyQt5',
    'PyQt6',
    'tkinter',
    'matplotlib',
    'numpy',  # Only exclude if you're not using it
    'scipy',
    'PIL',
    'cv2',
    'common.widgets.tracer',  # Exclude tracer module
]

# Analysis configuration
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate entries
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PesticideApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Add icon if you have one
    # icon='icon.ico',
)