"""
Season Planner V2 package for the LORENZO POZZI Pesticide App.

This package provides a completely rewritten season planner using proper Qt table
architecture (QTableView + QAbstractTableModel + QStyledItemDelegate) for clean,
Excel-like pesticide application management.

Key improvements over V1:
- Proper table interface instead of widget soup
- Excel-like editing behavior (double-click, F2, Tab navigation)
- Clean data/view separation
- Scalable performance
- Custom dialogs for complex inputs (products, UOMs)
- Import scenarios from Excel files
"""

from season_planner_page_v2.page_scenarios_manager import ScenariosManagerPage
from season_planner_page_v2.tab_scenario import ScenarioTabPage

# Import main widgets
from season_planner_page_v2.widgets.metadata_widget import SeasonPlanMetadataWidget
from season_planner_page_v2.widgets.applications_table import ApplicationsTableWidget
from season_planner_page_v2.widgets.eiq_summary import EIQSummaryWidget

# Import models
from season_planner_page_v2.models.application_table_model import ApplicationTableModel

# Import scenario functionality
from season_planner_page_v2.import_scenario import ImportScenarioDialog

__all__ = [
    # Main page and tabs
    'ScenariosManagerPage', 
    'ScenarioTabPage',
    
    # Widget components
    'SeasonPlanMetadataWidget',
    'ApplicationsTableWidget',
    'EIQSummaryWidget',
    
    # Models
    'ApplicationTableModel',
    
    # Import functionality
    'ImportScenarioDialog'
]