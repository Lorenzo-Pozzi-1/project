"""
Widgets package for Season Planner V2.

UI widgets for the new table-based season planner interface.
"""

from .metadata_widget import SeasonPlanMetadataWidget
from .applications_table import ApplicationsTableWidget
from .eiq_summary import EIQSummaryWidget

__all__ = [
    'SeasonPlanMetadataWidget',
    'ApplicationsTableWidget',
    'EIQSummaryWidget'
]