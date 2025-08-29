# STIR Module Documentation

**Acknoledgement:** This document was reviewed and edited by Lorenzo, but initially entirely produced by AI. 

## Overview

The STIR (Soil Tillage Intensity Rating) module provides a calculator for assessing soil disturbance intensity from tillage operations. It provides tools for creating scenarios, managing custom machines, and calculating STIR values based on operational parameters like depth, speed, and tillage type. This module implements the McCain internally modified USDA STIR methodology for quantifying tillage intensity impact on soil health, the formula is found and can be edited in the `data/model_operation.py` file in the `_calculate_single_tool_stir` method.

**Note**: This is a proof-of-concept implementation. The STIR value thresholds and intensity classifications should be validated and adjusted according to agronomy team recommendations before production deployment. The standard machines list has to be developed, I have merely produced some placeholders but this list should be compiled by an experienced agronomist.

## Module Structure

### Root Files

#### `__init__.py`
**Purpose**: Module initialization and public API definition  

#### `page_STIR_calculator.py`
**Purpose**: Main STIR calculator interface with tabbed scenario management  
**Key Components**:
- `STIRCalculatorPage` - Main page widget with scenario tabs
- `CustomSTIRTabBar` - Custom tab bar supporting double-click rename
- **Features**:
  - Multiple scenario management in tabs
  - UOM (Unit of Measure) selection for depth (inch/cm) and speed (mph/km/h)
  - Custom machine management integration
  - STIR score visualization with intensity ratings
  - Export and comparison functionality (To Be Developed)

**Dependencies**: 
- `STIRScenarioTabPage` for individual scenarios
- `CustomMachineManagerDialog` for machine management
- Common UI components (ScoreBar, ContentFrame, etc.)

#### `tab_scenario.py`
**Purpose**: Individual STIR scenario tab containing operations table  
**Key Components**:
- `STIRScenarioTabPage` - Single scenario widget
- **Features**:
  - Operations table integration
  - Scenario name management
  - UOM display settings
  - Real-time STIR calculation updates

**Dependencies**:
- `STIROperationsTableWidget` for operations management

## Data Layer

### `data/` Folder
Contains all data models and repositories for STIR calculations.

#### Core Models

##### `model_machine.py`
**Purpose**: Standard tillage machine definition  
**Key Classes**:
- `Machine` - Represents a standard tillage implement
- **Attributes**: name, depth, speed, surface area disturbed, tillage type factor, rotates (= PTO operated)
- **Methods**: `to_dict()`, `from_dict()`, `create_default_operation()`

        NOTE: this model represents the ones given for NA machines, so the width/depth% parameter is omitted! for questions about this contact Niek Engbers.

##### `model_operation.py`
**Purpose**: Individual field operation with STIR calculation logic  
**Key Classes**:
- `Operation` - Single tillage operation
- **Core Features**:
  - STIR calculation using McCain modified USDA formula
  - Support for both standard and custom machines
  - UOM conversion (depth: cm/inch, speed: km/h/mph)
  - Operation grouping (pre-plant, in-season, harvest)
  - Field fraction support for partial field operations

**STIR Calculation Formula**:

    NOTE: this formula represents the one given for NA machines, so the width/depth% parameter is omitted! for questions about this contact Niek Engbers. 

- **Non-rotating implements**: `STIR = (tillage_factor × 3.25) × (speed × 0.5) × depth × surface_fraction × field_fraction`
- **Rotating implements (PTO)**: `STIR = (tillage_factor × 3.25) × ((11 - speed) × 0.5) × depth × surface_fraction × field_fraction`

**Field Fraction Use Case**: The "% Field Tilled" parameter accommodates operations performed on only part of the field, such as for example using a ripper to break wheel compression lines left by harvest equipment in specific field areas.

##### `model_custom_machine.py`
**Purpose**: Multi-tool custom machine support  
**Key Classes**:
- `CustomMachine` - Custom machine with up to 10 tools
- `CustomMachineTool` - Individual tool on custom machine
- **Features**:
  - Tool-based STIR calculation (as dictated by the USDA)
  - Individual tool parameters (depth, surface area, tillage factor)
  - Machine-level properties (speed, notes, picture)

##### `model_season.py`
**Purpose**: Season/crop year container for operations  
**Key Classes**:
- `Season` - Collection of operations for a crop year
- **Features**:
  - Operation management (add, remove, reorder)
  - Total STIR calculation
  - Operation grouping by timing
  - Serialization support (i.e. from_dict, to_dict)

#### Data Access Layer

##### `repository_machine.py`
**Purpose**: Standard machine data repository  
**Key Classes**:
- `MachineRepository` - Singleton repository for standard machines
- **Data Source**: `csv_machines.csv`
- **Features**:
  - CSV loading with BOM handling
  - Machine filtering and search
  - Caching for performance

##### `repository_custom_machine.py`
**Purpose**: Custom machine persistence  
**Key Classes**:
- `CustomMachineRepository` - CRUD operations for custom machines
- **Data Source**: `csv_custom_machines.csv` Note that this may work well also as a .json file or as a set of .json files (one per machine, maybe one folder per machine with the json and picture inside) when the app is productionised, I leave the choice up to you.
- **Features**:
  - Flattened CSV storage (10 tool slots per machine)
  - Create, read, update, delete operations
  - Name-based machine lookup (we don't have machines data in GXCore so I went for name lookup, if in the future you introduce UIDs for machines as well modify the app to use that as well)

#### Data Files

##### `csv_machines.csv`

    NOTE: these should represent simple machines with individual tools (e.g. A chisel plow, A spring tine harrow, etc. if a machine has multiple tools, it needs to be created as a custom machine as the STIR chas to be calcualted for each individual tool).

**Purpose**: Standard machine database (I chose to go with a csv based system so that files are easily interpretable and modifiable by non-techincally-skilled humans as well, in case we want to give an agronomist the task to remake the machines list properly)
**Format**: Machine definitions with default parameters  
**Fields**: name, depth, depth_uom, speed, speed_uom, surface_area_disturbed, tillage_type_factor, picture, rotates

**Sample Machines**:
- Moldboard Plow (factor: 1.0) - Full inversion and mixing
- Chisel Plow (factor: 0.7) - Mixing without inversion
- Cambridge Roller (factor: 0.2) - Light compression
- Potato Harvester (factor: 1.0, rotating) - High disturbance with PTO

##### `csv_custom_machines.csv`
**Purpose**: User-created custom machine storage  
**Format**: Flattened structure with 10 tool slots per machine  
**Fields**: name, speed, speed_uom, picture, notes, tool1_name through tool10_tillage_type_factor

## Tillage Type Factors

The tillage type factor represents the soil disturbance intensity of different tillage operations:

- **1.0: Inversion + Mixing** - Complete soil inversion and mixing (moldboard plow, disk plow)
- **0.8: Mixing + Some Inversion** - Significant mixing with partial inversion (disk harrow, rotary hoe, hiller, planter)
- **0.7: Mixing Only** - Soil mixing without inversion (field cultivator, chisel plow, deep cultivator)
- **0.4: Lifting + Fracturing** - Subsurface fracturing with minimal surface disturbance (subsoiler, deep ripper)
- **0.15: Compression** - Soil compression with minimal disturbance (roller, cultipacker)

These factors are based on USDA STIR methodology.

## STIR Intensity Classifications

**Current Thresholds** (proof-of-concept values):
- **Light (0-100)**: Minimal soil disturbance, conservation tillage practices
- **Medium (100-300)**: Moderate disturbance, reduced tillage systems
- **Intense (300-600)**: High disturbance, conventional tillage
- **Very Intense (>600)**: Excessive disturbance, intensive tillage systems

**Visual Representation**:
- Light: Green (minimal impact)
- Medium: Yellow (moderate caution)
- Intense: Orange (high impact warning)
- Very Intense: Red (maximum impact alert)
        
        Note: These threshold values are placeholders for this proof-of-concept and should be calibrated with agronomy team expertise before production deployment.

### `data/images/` Folder
**Purpose**: Machine visualization assets for user interface

#### `machines/`
**Purpose**: Standard machine images  
**Contents**: Visual representations of standard tillage implements these are the placeholders I made:
- cambridge_roller.png, chisel_plow.png, deep_cultivator.png, fumigation_shank_rig.png
- hiller.png, moldboard_plow.png, potato_harvester.png, potato_planter.png
- power_harrow.png, rotavator.png, tandem_disc_harrow.png

**Usage**: Displayed in machine selection dialogs to help users intuitively identify equipment

#### `custom_machines/`

**Purpose**: User-uploaded custom machine photos (JPG format)  
**Contents**: Various user-provided machine images for custom equipment identification  
**Usage**: Displayed in custom machine manager and selection dialogs

## User Interface Components

### `operations_table/` Folder
**Purpose**: Operations table implementation using Model/View architecture

#### `widget_operations_table.py`
**Purpose**: Main table widget for operations display and editing  
**Key Classes**:
- `STIROperationsTableWidget` - Complete table widget
- **Features**:
  - Add/remove operations
  - Group-based visual organization
  - UOM-aware display
  - Real-time STIR updates
  - Machine selection integration

#### `model_operations_table.py`
**Purpose**: Qt table model for operations data  
**Key Classes**:
- `STIROperationsTableModel` - QAbstractTableModel implementation
- **Features**:
  - Grouped display (operations grouped by timing)
  - UOM conversion for display
  - Custom machine support
  - Group boundary detection for visual dividers

#### `delegates/` Folder
**Purpose**: Custom cell editors for table columns

##### `group_delegate.py`
**Purpose**: Operation group selection (pre-plant, in-season, harvest)  
**Key Classes**:
- `GroupSelectionDelegate` - Dropdown for operation timing classification

##### `machine_delegate.py`
**Purpose**: Machine selection with dialog integration  
**Key Classes**:
- `MachineSelectionDelegate` - Machine picker with standard/custom tabs
- **Features**: Preview images and integrated machine selection dialog

##### `numeric_delegate.py`
**Purpose**: Numeric input validation  
**Key Classes**:
- `NumericDelegate` - Validated numeric input for depth, speed, surface area, and field percentage

##### `group_divider_delegate.py`
**Purpose**: Visual group separation  
**Key Classes**:
- `GroupDividerDelegate` - Draws visual divider lines between operation groups

## Dialog Components

### `dialogs/` Folder
**Purpose**: Modal dialogs for machines management and selection for operations

#### `machine_selection_dialog.py`
**Purpose**: Machine picker dialog for the operations  
**Key Features**:
- Tabbed interface (Standard/Custom machines)
- Machine preview with images
- Integration with both machine repositories

#### `custom_machine_manager_dialog.py`
**Purpose**: Custom machine management interface  
**Key Classes**:
- `CustomMachineManagerDialog` - Main management dialog
- `CustomMachineCard` - Individual machine display cards
- **Features**:
  - Machine creation, editing, deletion
  - Visual machine cards
  - Direct integration with custom machine editor
  - Machine image display for easy identification

#### `custom_machine_editor_dialog.py`
**Purpose**: Custom machine creation and editing  
**Key Classes**:
- `CustomMachineEditorDialog` - Main editor dialog
- `ToolTabWidget` - Individual tool editor interface
- **Features**:
  - Machine-level properties (name, speed, picture upload)
  - Up to 10 tool tabs with drag-and-drop reordering
  - Tool-specific parameters (depth, tillage factor, surface area disturbed)
  - Interactive tillage factor help system
  - Photo upload and management

## Data Flow and Relationships

### Calculation Chain
1. **User Input**: Operations created through table interface
2. **Parameter Setting**: Machine selection --> load default parameters from repositories
3. **STIR Calculation**: `Operation.calculate_stir()`
4. **Aggregation**: Table model sums individual operations for total seasonal STIR
5. **Display**: Score bar shows intensity rating based on total with color-coded thresholds

### Machine Integration
1. **Standard Machines**: Loaded from CSV via `MachineRepository` with predefined parameters
2. **Custom Machines**: Created via editor interface, stored via `CustomMachineRepository`
3. **Operation Creation**: Both types create `Operation` instances with appropriate default parameters
    - The values displayed in the table for custom machines are the max depth out of the tools, the max surface area disturbed, and when one of the parameters is changed in the operation row of the table for a custom machine, it is applied to all the tools as such: e.g. the depth is modified from 10 to 5 cm --> for each individual tool the depth is reduced by 5 cm, the STIR is recalculated for the full custom machine. if a tool gets a depth < 0, it is assigned a value of 0 as it does no longer contibute to soil tillage if it's out of the gorund. 

### UOM Handling
- **Storage**: All data stored internally in metric units (cm, km/h)
- **Display**: Converted based on user preference (inch/cm, mph/km/h)
- **Conversion**: `Operation.get_depth_in_unit()` and `Operation.get_speed_in_unit()` methods

### File Dependencies
```
page_STIR_calculator.py
├── tab_scenario.py
│   └── operations_table/widget_operations_table.py
│       ├── model_operations_table.py
│       │   ├── data/model_operation.py
│       │   ├── data/repository_machine.py
│       │   └── data/repository_custom_machine.py
│       └── delegates/*.py
├── dialogs/custom_machine_manager_dialog.py
│   └── custom_machine_editor_dialog.py
│       └── data/model_custom_machine.py
└── dialogs/machine_selection_dialog.py
    ├── data/repository_machine.py
    └── data/repository_custom_machine.py
```

## Integration with Main Application

The STIR module integrates with the main PestIQ application through:

1. **Navigation**: Accessible from `HomePage` STIR tools section
2. **Main Window**: Added to page stack in `MainWindow` at index 5
3. **Preferences**: UOM settings synchronized with `user_preferences.json`
4. **Common Components**: Uses shared UI components from `common/` folder including ScoreBar

## Key Features Summary

- **Multi-scenario Management**: Tabbed interface for comparing different tillage strategies
- **Custom Machine Support**: Create complex multi-tool machines with individual tool parameters
- **Flexible UOM**: Switch between metric/imperial units with automatic conversion
- **Visual Organization**: Operations grouped by timing with clear visual separation
- **Real-time Calculation**: STIR values update immediately as parameters change
- **Machine Visualization**: Images displayed in selection dialogs for intuitive equipment identification
- **Extensible Design**: Clean separation between data models, business logic, and UI components
- **Partial Field Operations**: Support for operations affecting only portions of the field

## Future Development (Production Features)

- **Export Functionality**: Export scenarios and results to various formats
- **Scenario Comparison**: Side-by-side comparison of multiple tillage strategies
- **Threshold Calibration**: Agronomically-validated STIR intensity classifications
- **Advanced Reporting**: Detailed tillage impact analysis and recommendations  
- **Standard Machines**: Develop an appropriate list of standard machines for North America

## Technical Notes

- **NO USDA Compliance**: Implements McCain modified USDA STIR calculation methodology
- **Extensibility**: Modular design allows easy addition of new machine types and calculation methods
- **Data Persistence**: CSV-based storage with robust error handling and data validation
