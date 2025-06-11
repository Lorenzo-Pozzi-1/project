"""
Application Validator for the Season Planner.

Handles all validation logic for pesticide applications with clear state management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from data import Application, ProductRepository
from data.repository_AI import AIRepository


class ValidationState(Enum):
    """Clear validation states for applications."""
    VALID = "valid"
    VALID_ESTIMATED = "valid_estimated"  # Valid but using estimated EIQ
    INVALID_PRODUCT = "invalid_product"
    INVALID_DATA = "invalid_data"
    INCOMPLETE = "incomplete"


@dataclass
class ValidationIssue:
    """Individual validation issue."""
    field: str
    message: str
    severity: str  # 'error', 'warning', 'info'


@dataclass
class ValidationResult:
    """Result of application validation with support for multiple issues."""
    state: ValidationState
    issues: List[ValidationIssue]
    can_calculate_eiq: bool = False
    
    @property
    def message(self) -> str:
        """Get combined message from all issues."""
        if not self.issues:
            return "Application is valid"
        return "; ".join(issue.message for issue in self.issues)
    
    @property
    def primary_message(self) -> str:
        """Get the most important message."""
        if not self.issues:
            return "Application is valid"
        return self.issues[0].message


class ApplicationValidator:
    """
    Validator for pesticide applications with comprehensive validation logic.
    
    Handles validation state determination, issue tracking, and product verification.
    """
    
    def __init__(self):
        """Initialize the validator with repository access."""
        self._products_repo = ProductRepository.get_instance()
        self._ai_repo = AIRepository.get_instance()
    
    def validate_application(self, app: Application) -> ValidationResult:
        """
        Perform comprehensive validation with proper state hierarchy.
        
        Validation order:
        1. Check for missing required fields (INCOMPLETE)
        2. Validate data ranges and formats (INVALID_DATA)  
        3. Check product existence (INVALID_PRODUCT)
        4. Check EIQ calculation capability and AI data completeness (VALID/VALID_ESTIMATED)
        """
        issues = []
        
        # 1. INCOMPLETE STATE: Check for missing required fields
        missing_fields = []
        if not app.product_name or not app.product_name.strip():
            missing_fields.append("product name")
        if not app.rate or app.rate <= 0:
            missing_fields.append("application rate")
        if not app.rate_uom or not app.rate_uom.strip():
            missing_fields.append("rate unit")
        
        if missing_fields:
            issues.append(ValidationIssue(
                field="required_fields",
                message=f"Missing required fields: {', '.join(missing_fields)}",
                severity="error"
            ))
            return ValidationResult(ValidationState.INCOMPLETE, issues, False)
        
        # 2. INVALID_DATA STATE: Validate data ranges and formats
        if app.rate is not None and app.rate < 0:
            issues.append(ValidationIssue(
                field="rate",
                message="Application rate cannot be negative",
                severity="error"
            ))
        
        if app.area is not None and app.area < 0:
            issues.append(ValidationIssue(
                field="area",
                message="Application area cannot be negative", 
                severity="error"
            ))
        
        # Check for unreasonably high values
        if app.rate is not None and app.rate > 10000:
            issues.append(ValidationIssue(
                field="rate",
                message="Application rate seems unusually high - please verify",
                severity="warning"
            ))
        
        if issues:
            return ValidationResult(ValidationState.INVALID_DATA, issues, False)
        
        # 3. INVALID_PRODUCT STATE: Check product existence
        product = self._find_product(app.product_name)
        if not product:
            issues.append(ValidationIssue(
                field="product_name",
                message=f"Product '{app.product_name}' not found in database",
                severity="error"
            ))
            return ValidationResult(ValidationState.INVALID_PRODUCT, issues, False)
        
        # 4. VALID/VALID_ESTIMATED STATE: Check EIQ calculation capability
        can_calculate_eiq = (
            app.product_name and app.product_name.strip() and
            app.rate and app.rate > 0 and
            app.rate_uom and app.rate_uom.strip() and
            product is not None
        )
        
        if not can_calculate_eiq:
            issues.append(ValidationIssue(
                field="eiq",
                message="Application is valid but EIQ calculation requires additional data",
                severity="warning"
            ))
            return ValidationResult(ValidationState.VALID, issues, False)
        
        # Check if product has active ingredients and their EIQ completeness
        ai_data = product.get_ai_data()
        if not ai_data:
            # No AI data at all - use estimated EIQ
            issues.append(ValidationIssue(
                field="eiq",
                message="Application is valid but uses estimated EIQ (product lacks AI data)",
                severity="info"
            ))
            return ValidationResult(ValidationState.VALID_ESTIMATED, issues, True)
        
        # Check if any active ingredients are missing EIQ values
        missing_eiq_ais = []
        for ai in ai_data:
            ai_name = ai.get('name')
            if ai_name:
                ai_eiq = self._ai_repo.get_ai_eiq(ai_name)
                if ai_eiq is None:  # Missing EIQ value (None, not 0)
                    missing_eiq_ais.append(ai_name)
        
        if missing_eiq_ais:
            # Some AIs are missing EIQ values - use estimated EIQ
            ai_list = ', '.join(missing_eiq_ais)
            issues.append(ValidationIssue(
                field="eiq",
                message=f"Application uses estimated EIQ (missing EIQ data for: {ai_list})",
                severity="info"
            ))
            return ValidationResult(ValidationState.VALID_ESTIMATED, issues, True)
        
        # All validations passed and all AIs have EIQ values
        issues.append(ValidationIssue(
            field="status",
            message="Application is valid and EIQ can be calculated",
            severity="info"
        ))
        return ValidationResult(ValidationState.VALID, issues, True)
    
    def get_validation_summary(self, applications: List[Application]) -> dict:
        """Get a summary of validation states across all applications."""
        summary = {
            ValidationState.VALID: 0,
            ValidationState.VALID_ESTIMATED: 0,
            ValidationState.INVALID_PRODUCT: 0,
            ValidationState.INVALID_DATA: 0,
            ValidationState.INCOMPLETE: 0
        }
        
        for app in applications:
            validation = self.validate_application(app)
            summary[validation.state] += 1
        
        return summary
    
    def format_validation_status(self, validation: ValidationResult) -> str:
        """Format validation status for display with issue count."""
        status_map = {
            ValidationState.VALID: "✓ Valid",
            ValidationState.VALID_ESTIMATED: "✓ Valid (Est.)",
            ValidationState.INVALID_PRODUCT: "✗ Invalid Product", 
            ValidationState.INVALID_DATA: "⚠ Invalid Data",
            ValidationState.INCOMPLETE: "◯ Incomplete"
        }
        
        base_status = status_map.get(validation.state, "Unknown")
        
        # Add issue count for non-valid states
        if validation.state not in [ValidationState.VALID, ValidationState.VALID_ESTIMATED] and len(validation.issues) > 1:
            base_status += f" ({len(validation.issues)} issues)"
        
        return base_status
    
    def _find_product(self, product_name: str):
        """Find a product by name in the filtered products list."""
        try:
            if not product_name:
                return None
            
            filtered_products = self._products_repo.get_filtered_products()
            for product in filtered_products:
                if product.product_name == product_name:
                    return product
            return None
        except Exception as e:
            print(f"Error in _find_product(): {e}")
            return None