"""
Season Planner package for the LORENZO POZZI Pesticide App.

This package provides a completely rewritten season planner using proper Qt table
architecture (QTableView + QAbstractTableModel + QStyledItemDelegate) for clean,
Excel-like pesticide application management.
"""

from season_planner_page.page_scenarios_manager import ScenariosManagerPage
from season_planner_page.tab_scenario import ScenarioTabPage

# Import main widgets
from season_planner_page.widgets.metadata_widget import SeasonPlanMetadataWidget
from season_planner_page.widgets.applications_table import ApplicationsTableWidget
from season_planner_page.widgets.eiq_summary import EIQSummaryWidget

# Import models
from season_planner_page.models.application_table_model import ApplicationTableModel

# Import scenario functionality
from season_planner_page.import_export import ImportScenarioDialog

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