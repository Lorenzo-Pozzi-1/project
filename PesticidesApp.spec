# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Increase the recursion limit
sys.setrecursionlimit(sys.getrecursionlimit() * 5)

# Get the current directory (where main.py is located)
project_root = os.path.dirname(os.path.abspath('main.py'))

# Define data files to include
data_files = [
    # Config file
    ('user_preferences.json', '.'),
    
    # Data CSV files
    ('data/csv_AI.csv', 'data'),
    ('data/csv_products.csv', 'data'),
    ('data/csv_UOM.csv', 'data'),
    
    # User manual files - include entire directory for CSS/JS/images
    ('user_manual', 'user_manual'),
]

# Hidden imports - optimized for openpyxl only
hidden_imports = [
    # PySide6 modules - only what you use
    'PySide6.QtCore',
    'PySide6.QtWidgets',
    'PySide6.QtGui',
    'PySide6.QtPrintSupport',
    
    # Your app modules only
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
    'common.widgets.uom_selector',
    'common.widgets.tracer',
    
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
    
    'user_manual',
    'user_manual.user_manual_dialog',
    
    # Browser launching dependencies
    'webbrowser',
    'tempfile',
    'shutil',
    
    # Essential dependencies - openpyxl focused
    'openpyxl',
    'openpyxl.workbook',
    'openpyxl.worksheet',
    'openpyxl.cell',
    'openpyxl.styles',
    'openpyxl.utils',
    'openpyxl.reader',
    'openpyxl.writer',
    'openpyxl.cell._writer',
    'openpyxl.worksheet._writer',
    'openpyxl.workbook.child',
    'openpyxl.workbook.defined_name',
    'openpyxl.workbook.external_link',
    'openpyxl.workbook.function_group',
    'openpyxl.workbook.smart_tags',
    'openpyxl.workbook.views',
    'openpyxl.workbook.web',
    'json',
    'csv',
    'datetime',
    'typing',
    'dataclasses',
    'collections',
    'traceback',
    'pathlib',
    'os',
    'sys',
    'io',
    'itertools',
    'functools',
    'operator',
    're',
]

# Comprehensive excludes - now including pandas and its entire ecosystem
excludes = [
    
    # PySide6 modules not used - QtWebEngine explicitly excluded
    'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtNetwork',

    'PySide6.QtOpenGL',
    'PySide6.QtSql',
    'PySide6.QtTest',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtCharts',
    'PySide6.QtDataVisualization',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DRender',
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuickWidgets',
    'PySide6.QtSvg',
    'PySide6.QtXml',
    'PySide6.QtHelp',
    'PySide6.QtDesigner',
    'PySide6.QtUiTools',
    'PySide6.QtBluetooth',
    'PySide6.QtNfc',
    'PySide6.QtPositioning',
    'PySide6.QtLocation',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtWebChannel',
    'PySide6.QtWebSockets',
    'PySide6.QtRemoteObjects',
    'PySide6.QtScxml',
    'PySide6.QtStateMachine',
    'PySide6.QtConcurrent',
    'PySide6.QtAxContainer',
    'PySide6.QtWinExtras',
    
    # Pandas and all its dependencies
    'pandas',
    'numpy',
    'scipy',
    'pytz',
    'dateutil',
    'xlrd',
    'xlwt',
    'xlsxwriter',
    
    # Data science ecosystem
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    'altair',
    'statsmodels',
    'sklearn',
    'skimage',
    'patsy',
    'scipy.stats',
    'scipy.optimize',
    'scipy.sparse',
    'scipy.linalg',
    
    # Scientific computing
    'sympy',
    'astropy',
    'numba',
    'llvmlite',
    'h5py',
    'tables',
    'pyarrow',
    'xarray',
    'dask',
    'distributed',
    'fastparquet',
    
    # ML/AI frameworks
    'tensorflow',
    'torch',
    'transformers',
    'cv2',
    'PIL',
    'Pillow',
    'opencv',
    
    # Web frameworks and networking
    'flask',
    'django',
    'fastapi',
    'tornado',
    'selenium',
    'requests',
    'urllib3',
    'aiohttp',
    'httpx',
    
    # Jupyter ecosystem
    'IPython',
    'jupyter',
    'jupyterlab',
    'notebook',
    'nbconvert',
    'nbformat',
    'ipywidgets',
    'ipykernel',
    'traitlets',
    
    # Documentation/dev tools
    'sphinx',
    'docutils',
    'babel',
    'jinja2',
    'markdown',
    'mistune',
    'pygments',
    'mako',
    
    # Other GUI frameworks
    'PySide5',
    'PyQt5',
    'PyQt6',
    'shiboken5',
    'tkinter',
    'wx',
    'gi',
    'kivy',
    
    # Database drivers
    'sqlalchemy',
    'psycopg2',
    'MySQLdb',
    'sqlite3',
    'botocore',
    'pymongo',
    'redis',
    
    # Development/testing
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'cProfile',
    'profile',
    'coverage',
    'mock',
    
    # Cloud/networking/crypto
    'paramiko',
    'cryptography',
    'bcrypt',
    'nacl',
    'zmq',
    'certifi',
    'charset_normalizer',
    'idna',
    'urllib3',
    
    # Heavy utility packages
    'lxml',
    'beautifulsoup4',
    'html5lib',
    'wheel',
    'setuptools',
    'pkg_resources',
    'platformdirs',
    'zipp',
    'importlib_metadata',
    'ruamel',
    'cloudpickle',
    'fsspec',
    'intake',
    'panel',
    'pyviz_comms',
    'anyio',
    'jsonschema',
    'jsonschema_specifications',
    'pywt',
    'imageio',
    'tifffile',
    'psutil',
    'py',
    'more_itertools',
    'jaraco',
    'backports',
    'typing_extensions',
    'importlib_resources',
    'tomli',
    'zoneinfo',
    'packaging',
    'distutils',
    
    # Pandas-specific modules that might be auto-imported
    'pandas.core',
    'pandas.io',
    'pandas.plotting',
    'pandas.api',
    'pandas.arrays',
    'pandas.compat',
    'pandas.errors',
    'pandas.tseries',
    'pandas.util',
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

# Filter out unwanted directories
def filter_data(data_list):
    """Filter out unwanted data files and directories."""
    filtered = []
    for item in data_list:
        if isinstance(item, tuple) and len(item) >= 2:
            source_path = item[0]
            # Exclude unwanted directories, pandas remnants, and cache
            if (
                'test_data' not in source_path and 
                'update_products' not in source_path and
                '__pycache__' not in source_path and
                'pandas' not in source_path.lower() and
                'numpy' not in source_path.lower() and
                'scipy' not in source_path.lower() and
                not source_path.endswith('.docx')
            ):
                filtered.append(item)
    return filtered

# Apply filtering
a.datas = filter_data(a.datas)

# Remove Qt translation files - this saves ~2-3MB
a.datas = [x for x in a.datas if not (x[0].startswith('PySide6/translations/') and x[0].endswith('.qm'))]

# Remove some unnecessary Qt plugins (keeping minimal set for functionality)
qt_plugins_to_remove = [
    'PySide6/plugins/generic/qtuiotouchplugin.dll',
    'PySide6/plugins/platforminputcontexts/qtvirtualkeyboardplugin.dll',
]
a.datas = [x for x in a.datas if x[0] not in qt_plugins_to_remove]

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
    name='PesticidesApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'PySide6/Qt6Core.dll',
        'PySide6/Qt6Gui.dll', 
        'PySide6/Qt6Widgets.dll',
        'PySide6/Qt6PrintSupport.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)