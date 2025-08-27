"""
Application Validator for the Season Planner.

Handles all validation logic for pesticide applications with clear state management.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List
from PySide6.QtWidgets import QMessageBox
from data.model_application import Application
from data.repository_product import ProductRepository
from data.repository_AI import AIRepository


class ValidationState(Enum):
    """Clear validation states for applications."""
    VALID = "valid"
    VALID_ESTIMATED = "valid_estimated"  # Valid but using estimated EIQ
    RATE_ISSUES = "rate_issues"  # Valid but rate outside label recommendations
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
        1. Check product existence (INVALID_PRODUCT)
        2. Skip validation for adjuvants (they don't contribute to EIQ)
        3. Check for missing required fields (INCOMPLETE)
        4. Validate data ranges (INVALID_DATA)
        5. Validate rate against label limits (RATE_ISSUES)
        6. Check EIQ calculation capability and AI data completeness (VALID/VALID_ESTIMATED)
        """
        issues = []
        
        # 1. INVALID_PRODUCT STATE: Check product existence
        # if name is missing, mark as INCOMPLETE
        if not app.product_name or not app.product_name.strip(): 
            issues.append(ValidationIssue(
                field="product_name",
                message="Product name is required",
                severity="error"
            ))
            return ValidationResult(ValidationState.INCOMPLETE, issues, False)
        
        product = self._find_product(app.product_name)
        if not product:
            issues.append(ValidationIssue(
                field="product_name",
                message=f"Product '{app.product_name}' not found in database",
                severity="error"
            ))
            return ValidationResult(ValidationState.INVALID_PRODUCT, issues, False)

        # 2. Skip validation for adjuvants - they don't contribute to EIQ
        if self._is_adjuvant_or_biological(product):
            issues.append(ValidationIssue(
                field="status",
                message="Adjuvant (or biological, US only) product - excluded from EIQ calculations",
                severity="info"
            ))
            return ValidationResult(ValidationState.VALID, issues, True)

        # 3. INCOMPLETE STATE: Check for missing required fields
        missing_fields = []
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

        # 4. INVALID_DATA STATE: Validate data ranges
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
        
        # Check for invalid data issues first (excluding rate validation)
        data_issues = [issue for issue in issues if issue.severity == "error"]
        if data_issues:
            return ValidationResult(ValidationState.INVALID_DATA, issues, False)
        
        # 5. RATE_ISSUES STATE: Validate application rate against label limits
        rate_issue = None
        if app.rate is not None:
            rate_issue = self._validate_rate_against_label(app.rate, app.rate_uom, product)
            if rate_issue:
                issues.append(rate_issue)
                # Return RATE_ISSUES state but still allow EIQ calculation
                return ValidationResult(ValidationState.RATE_ISSUES, issues, True)

        # 6. VALID/VALID_ESTIMATED STATE: Check EIQ calculation capability
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
    
    def _validate_rate_against_label(self, app_rate: float, app_rate_uom: str, product) -> ValidationIssue:
        """
        Validate application rate against product label limits.
        
        Args:
            app_rate: Application rate from the application
            app_rate_uom: Application rate UOM
            product: Product object with label_minimum_rate and label_maximum_rate
            
        Returns:
            ValidationIssue or None if validation passes
        """
        min_rate = product.label_minimum_rate
        max_rate = product.label_maximum_rate
        
        # Skip validation if no label rates are available
        if min_rate is None and max_rate is None:
            return None
        
        label_rate_uom = getattr(product, 'rate_uom', None)
        if not label_rate_uom or not app_rate_uom:
            # Can't validate without knowing both UOMs
            return None
        
        # Convert application rate to label UOM for comparison
        try:
            from data.repository_UOM import UOMRepository, CompositeUOM
            from common.utils import get_preferences_manager
            
            uom_repo = UOMRepository.get_instance()
            user_preferences = get_preferences_manager().get_section("user_preferences", {})
            
            # Only convert if UOMs are different
            if app_rate_uom != label_rate_uom:
                from_composite = CompositeUOM(app_rate_uom)
                to_composite = CompositeUOM(label_rate_uom)
                
                converted_app_rate = uom_repo.convert_composite_uom(
                    app_rate, from_composite, to_composite, user_preferences
                )
            else:
                converted_app_rate = app_rate
                
        except Exception as e:
            # If conversion fails, we can't validate - log the issue but don't block
            QMessageBox.warning(None, "Warning", f"Could not convert rate units for validation: {app_rate_uom} -> {label_rate_uom}: {e}")
            return None
        
        # Now compare converted rate with label rates
        # Condition 1: Max rate exists and app.rate >= max * 1.1
        if max_rate is not None and converted_app_rate >= max_rate * 1.1:
            return ValidationIssue(
                field="rate",
                message=f"Application rate ({converted_app_rate:.2f} {label_rate_uom}) exceeds label maximum ({max_rate} {label_rate_uom}) by >10%\nWARNING: the field EIQ for this product is still included in the total season EIQ calculation.",
                severity="info"
            )
        
        # Condition 2: Min rate exists and app.rate <= min * 0.8
        if min_rate is not None and converted_app_rate <= min_rate * 0.8:
            return ValidationIssue(
                field="rate",
                message=f"Application rate ({converted_app_rate:.2f} {label_rate_uom}) is below label minimum ({min_rate} {label_rate_uom}) by >20%\nWARNING: the field EIQ for this product is still included in the total season EIQ calculation.",
                severity="info"
            )
        
        # Condition 3: Min rate doesn't exist and app.rate <= max * 0.25
        if min_rate is None and max_rate is not None and converted_app_rate <= max_rate * 0.25:
            return ValidationIssue(
                field="rate",
                message=f"Application min rate is not available from the label and \n({converted_app_rate:.2f} {label_rate_uom}) is much lower (less than 1/4th) than the label maximum ({max_rate} {label_rate_uom})",
                severity="info"
            )
        
        return None
    
    def get_validation_summary(self, applications: List[Application]) -> dict:
        """Get a summary of validation states across all applications."""
        summary = {
            ValidationState.VALID: 0,
            ValidationState.VALID_ESTIMATED: 0,
            ValidationState.RATE_ISSUES: 0,
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
            ValidationState.RATE_ISSUES: "⚠ Check Rate",
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
            QMessageBox.warning(None, "Error", f"Error in ApplicationValidator._find_product() method: {e}")
            return None
    
    def _is_adjuvant_or_biological(self, product) -> bool:
        """
        Check if a product is an adjuvant or biological based on product type or application method.

        Args:
            product: Product object to check
            
        Returns:
            bool: True if product is an adjuvant or biological, False otherwise
        """
        if not product:
            return False
        
        # Check product type
        if hasattr(product, 'product_type') and product.product_type:
            if product.product_type.lower() == "adjuvant" or product.product_type.lower() == "biological":
                return True
                
        # Check application method
        if hasattr(product, 'application_method') and product.application_method:
            if product.application_method.lower() == "adjuvant":
                return True
                
        return False