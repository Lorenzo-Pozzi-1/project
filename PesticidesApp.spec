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
    
    # User manual files
    ('user_manual/*', 'user_manual'),
]

# Hidden imports - modules that PyInstaller might miss
hidden_imports = [
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',
    
    # Common modules
    'common',
    'common.constants',
    'common.styles',
    'common.utils',
    'common.calculations',
    'common.calculations.layer_1_interface',
    'common.widgets',
    'common.widgets.header_frame_buttons',
    'common.widgets.product_selection',
    'common.widgets.application_params',
    'common.widgets.scorebar',
    'common.widgets.UOM_selector',
    'common.widgets.tracer',
    
    # Data modules
    'data',
    'data.model_AI',
    'data.model_application',
    'data.model_product',
    'data.model_scenario',
    'data.repository_AI',
    'data.repository_product',
    'data.repository_UOM',
    
    # Main page modules
    'main_page',
    'main_page.window_main',
    'main_page.page_home',
    'main_page.widget_preferences_row',
    
    # Products page modules
    'products_page',
    'products_page.page_products',
    'products_page.tab_products_list',
    'products_page.tab_products_comparison',
    'products_page.widget_filter_row',
    'products_page.widget_products_table',
    'products_page.widget_comparison_table',
    
    # EIQ Calculator page modules
    'eiq_calculator_page',
    'eiq_calculator_page.page_eiq_calculator',
    'eiq_calculator_page.tab_single_calculator',
    'eiq_calculator_page.tab_multi_calculator',
    'eiq_calculator_page.widget_product_card',
    'eiq_calculator_page.widgets_results_display',
    
    # Season planner page modules
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
    
    # User manual module
    'user_manual',
    'user_manual.user_manual_dialog',
        
    # Standard library modules that might be needed
    'pandas',
    'openpyxl',
    'json',
    'datetime',
    'typing',
    'dataclasses',
    'collections',
    'traceback',
    'pathlib',
]

# Exclude unwanted modules and test data
excludes = [
    # Exclude Qt5 completely as requested
    'PySide5',
    'PyQt5',
    'shiboken5',
    
    # Other GUI frameworks
    'tkinter',
    'wx',
    'gi',
    
    # Heavy libraries not needed
    'matplotlib',
    'numpy',
    'scipy',
    'PIL',
    'cv2',
    'sklearn',
    'tensorflow',
    'torch',
    
    # Development/testing modules
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'cProfile',
    'profile',
    
    # IDE specific
    'IPython',
    'jupyter',
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

# Filter out test_data and other unwanted directories
def filter_data(data_list):
    """Filter out unwanted data files and directories."""
    filtered = []
    for item in data_list:
        if isinstance(item, tuple) and len(item) >= 2:
            source_path = item[0]
            # Exclude test_data directory and its contents
            if 'test_data' not in source_path and '__pycache__' not in source_path:
                filtered.append(item)
    return filtered

# Apply filtering
a.datas = filter_data(a.datas)

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