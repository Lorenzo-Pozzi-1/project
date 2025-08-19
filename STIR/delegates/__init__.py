"""
Delegates package for STIR module.

Custom QStyledItemDelegate implementations for different data types
in the STIR operations table.
"""

from .machine_delegate import MachineSelectionDelegate
from .group_delegate import GroupSelectionDelegate
from .numeric_delegate import NumericDelegate

__all__ = [
    'MachineSelectionDelegate',
    'GroupSelectionDelegate',
    'NumericDelegate'
]