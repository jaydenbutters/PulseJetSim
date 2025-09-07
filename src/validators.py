"""
Input validation functions for the pulse jet modeler

This module provides comprehensive validation functions for all input parameters
used in pulse jet engine design and analysis. It includes range checks, logical
consistency validation, engineering reasonableness checks, and safety limits.

The validators ensure that:
- All inputs are within physically reasonable ranges
- Parameter combinations make engineering sense
- Safety limits are respected
- Common design mistakes are caught early

Functions:
    Geometry Validation:
        - validate_geometry_parameters: Complete geometry validation
        - validate_combustion_chamber: Chamber-specific checks
        - validate_intake_exhaust: Intake/exhaust validation
    
    Valve System Validation:
        - validate_valve_parameters: Valve system validation
        - validate_valve_areas: Area-based checks
        - validate_valve_compatibility: Type-specific validation
    
    Operating Conditions:
        - validate_operating_conditions: Operating parameter validation
        - validate_fuel_parameters: Fuel-specific checks
        - validate_environmental_conditions: Ambient condition checks
    
    Comprehensive Validation:
        - validate_all_parameters: Complete system validation
        - validate_design_safety: Safety limit checks
        - validate_manufacturing_feasibility: Manufacturability checks

Example:
    Basic validation:
    
    >>> from validators import validate_geometry_parameters
    >>> 
    >>> is_valid, errors = validate_geometry_parameters(
    ...     length=50, diameter=15, intake_dia=8, 
    ...     exhaust_dia=10, exhaust_length=80
    ... )
    >>> 
    >>> if not is_valid:
    ...     for error in errors:
    ...         print(f"Error: {error}")

Author: Pulse Jet Modeler Contributors
License: MIT
Version: 1.0.0
"""

import math
import warnings
from typing import Tuple, Union, Any, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

# Try to import streamlit for UI functions, with fallback
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False
    # Create mock streamlit functions
    class MockStreamlit:
        @staticmethod
        def warning(msg): warnings.warn(msg)
        @staticmethod
        def error(msg): print(f"ERROR: {msg}")
        @staticmethod
        def success(msg): print(f"SUCCESS: {msg}")
        @staticmethod
        def info(msg): print(f"INFO: {msg}")
    st = MockStreamlit()


class ValidationLevel(Enum):
    """Validation strictness levels"""
    STRICT = "strict"           # Tight engineering limits
    NORMAL = "normal"          # Reasonable design limits  
    PERMISSIVE = "permissive"  # Wide experimental limits


class ValidationCategory(Enum):
    """Categories of validation errors"""
    CRITICAL = "critical"      # Will cause calculation failure
    WARNING = "warning"        # May cause poor performance
    INFO = "info"             # Design recommendations


@dataclass
class ValidationResult:
    """Structured validation result"""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    info: List[str]
    category: ValidationCategory = ValidationCategory.INFO
    
    def add_error(self, message: str, category: ValidationCategory = ValidationCategory.CRITICAL):
        """Add an error message with category"""
        if category == ValidationCategory.CRITICAL:
            self.errors.append(message)
            self.is_valid = False
        elif category == ValidationCategory.WARNING:
            self.warnings.append(message)
        else:
            self.info.append(message)
    
    def merge(self, other: 'ValidationResult'):
        """Merge another validation result"""
        if not other.is_valid:
            self.is_valid = False
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)


# Validation Constants and Limits
class ValidationLimits:
    """Validation limits for different parameters"""
    
    # Geometry limits (cm)
    GEOMETRY_LIMITS = {
        ValidationLevel.STRICT: {
            'combustion_chamber_length': (15, 80),
            'combustion_chamber_diameter': (8, 25),
            'intake_diameter': (3, 12),
            'exhaust_diameter': (4, 18),
            'exhaust_length': (30, 150),
            'ld_ratio': (2.0, 5.0),
            'area_ratio': (1.0, 3.0)
        },
        ValidationLevel.NORMAL: {
            'combustion_chamber_length': (10, 100),
            'combustion_chamber_diameter': (5, 30),
            'intake_diameter': (2, 15),
            'exhaust_diameter': (3, 20),
            'exhaust_length': (20, 200),
            'ld_ratio': (1.5, 6.0),
            'area_ratio': (0.8, 4.0)
        },
        ValidationLevel.PERMISSIVE: {
            'combustion_chamber_length': (5, 200),
            'combustion_chamber_diameter': (3, 50),
            'intake_diameter': (1, 25),
            'exhaust_diameter': (2, 40),
            'exhaust_length': (10, 300),
            'ld_ratio': (0.5, 10.0),
            'area_ratio': (0.3, 8.0)
        }
    }
    
    # Valve limits
    VALVE_LIMITS = {
        ValidationLevel.STRICT: {
            'num_valves': (2, 8),
            'valve_area': (8, 40),
            'valve_to_intake_ratio': (0.6, 1.5)
        },
        ValidationLevel.NORMAL: {
            'num_valves': (1, 12),
            'valve_area': (5, 50),
            'valve_to_intake_ratio': (0.4, 2.0)
        },
        ValidationLevel.PERMISSIVE: {
            'num_valves': (1, 20),
            'valve_area': (2, 100),
            'valve_to_intake_ratio': (0.2, 4.0)
        }
    }
    
    # Operating condition limits
    OPERATING_LIMITS = {
        ValidationLevel.STRICT: {
            'ambient_pressure': (95, 110),
            'ambient_temp': (0, 40),
            'air_fuel_ratio_tolerance': 0.2
        },
        ValidationLevel.NORMAL: {
            'ambient_pressure': (80, 120),
            'ambient_temp': (-20, 50),
            'air_fuel_ratio_tolerance': 0.3
        },
        ValidationLevel.PERMISSIVE: {
            'ambient_pressure': (50, 150),
            'ambient_temp': (-50, 80),
            'air_fuel_ratio_tolerance': 0.5
        }
    }


# Geometry Validation Functions
def validate_geometry_parameters(length: float, diameter: float, intake_dia: float, 
                               exhaust_dia: float, exhaust_length: float,
                               validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Tuple[bool, List[str]]:
    """
    Validate engine geometry parameters with comprehensive checks
    
    Args:
        length (float): Combustion chamber length (cm)
        diameter (float): Combustion chamber diameter (cm)
        intake_dia (float): Intake diameter (cm)
        exhaust_dia (float): Exhaust diameter (cm)
        exhaust_length (float): Exhaust length (cm)
        validation_level (ValidationLevel): Strictness of validation
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    result = ValidationResult(True, [], [], [])
    limits = ValidationLimits.GEOMETRY_LIMITS[validation_level]
    
    # Basic range validation
    _validate_parameter_range(result, "Combustion chamber length", length, 
                            limits['combustion_chamber_length'], "cm")
    _validate_parameter_range(result, "Combustion chamber diameter", diameter, 
                            limits['combustion_chamber_diameter'], "cm")
    _validate_parameter_range(result, "Intake diameter", intake_dia, 
                            limits['intake_diameter'], "cm")
    _validate_parameter_range(result, "Exhaust diameter", exhaust_dia, 
                            limits['exhaust_diameter'], "cm")
    _validate_parameter_range(result, "Exhaust length", exhaust_length, 
                            limits['exhaust_length'], "cm")
    
    # Logical consistency checks
    if intake_dia >= diameter:
        result.add_error("Intake diameter must be smaller than combustion chamber diameter")
    
    if exhaust_dia > diameter * 1.2:
        result.add_error(f"Exhaust diameter ({exhaust_dia:.1f} cm) is too large relative to chamber diameter ({diameter:.1f} cm)")
    
    # L/D ratio validation
    if diameter > 0:
        ld_ratio = length / diameter
        ld_min, ld_max = limits['ld_ratio']
        if ld_ratio < ld_min:
            result.add_error(f"L/D ratio ({ld_ratio:.1f}) is too low (minimum {ld_min:.1f}) - may cause incomplete combustion")
        elif ld_ratio > ld_max:
            result.add_error(f"L/D ratio ({ld_ratio:.1f}) is too high (maximum {ld_max:.1f}) - may cause excessive heat loss")
        elif ld_ratio < ld_min * 1.2:
            result.add_error(f"L/D ratio ({ld_ratio:.1f}) is borderline low - consider increasing length", ValidationCategory.WARNING)
        elif ld_ratio > ld_max * 0.8:
            result.add_error(f"L/D ratio ({ld_ratio:.1f}) is borderline high - may reduce efficiency", ValidationCategory.WARNING)
    
    # Area ratio validation
    if intake_dia > 0:
        intake_area = math.pi * (intake_dia/2)**2
        exhaust_area = math.pi * (exhaust_dia/2)**2
        area_ratio = exhaust_area / intake_area
        
        area_min, area_max = limits['area_ratio']
        if area_ratio < area_min:
            result.add_error(f"Exhaust/intake area ratio ({area_ratio:.2f}) is too low - may restrict flow")
        elif area_ratio > area_max:
            result.add_error(f"Exhaust/intake area ratio ({area_ratio:.2f}) is too high - may affect resonance tuning")
    
    # Engineering reasonableness checks
    _validate_combustion_chamber_geometry(result, length, diameter, validation_level)
    _validate_intake_exhaust_geometry(result, intake_dia, exhaust_dia, exhaust_length, validation_level)
    
    return result.is_valid, result.errors + result.warnings


def _validate_combustion_chamber_geometry(result: ValidationResult, length: float, diameter: float,
                                        validation_level: ValidationLevel):
    """Validate combustion chamber specific geometry"""
    if length <= 0 or diameter <= 0:
        return
    
    # Volume calculations
    volume_liters = math.pi * (diameter/2)**2 * length / 1000
    
    # Volume reasonableness
    if volume_liters < 0.05:
        result.add_error(f"Combustion volume ({volume_liters:.3f} L) is very small - may have poor combustion", 
                        ValidationCategory.WARNING)
    elif volume_liters > 50:
        result.add_error(f"Combustion volume ({volume_liters:.1f} L) is very large - consider weight implications", 
                        ValidationCategory.WARNING)
    
    # Surface area to volume ratio
    surface_area = 2 * math.pi * (diameter/2)**2 + math.pi * diameter * length  # cm²
    sa_to_vol_ratio = surface_area / volume_liters  # cm²/L
    
    if sa_to_vol_ratio > 2000:
        result.add_error(f"High surface area to volume ratio ({sa_to_vol_ratio:.0f} cm²/L) - may cause excessive heat loss", 
                        ValidationCategory.WARNING)
    elif sa_to_vol_ratio < 200:
        result.add_error(f"Low surface area to volume ratio ({sa_to_vol_ratio:.0f} cm²/L) - may have poor heat transfer", 
                        ValidationCategory.INFO)


def _validate_intake_exhaust_geometry(result: ValidationResult, intake_dia: float, 
                                    exhaust_dia: float, exhaust_length: float,
                                    validation_level: ValidationLevel):
    """Validate intake and exhaust specific geometry"""
    
    # Exhaust length to diameter ratio
    if exhaust_dia > 0:
        exhaust_ld_ratio = exhaust_length / exhaust_dia
        
        if exhaust_ld_ratio < 3:
            result.add_error(f"Exhaust L/D ratio ({exhaust_ld_ratio:.1f}) is very low - may cause poor expansion", 
                            ValidationCategory.WARNING)
        elif exhaust_ld_ratio > 20:
            result.add_error(f"Exhaust L/D ratio ({exhaust_ld_ratio:.1f}) is very high - may cause excessive friction losses", 
                            ValidationCategory.WARNING)
    
    # Flow velocity estimates
    if intake_dia > 0 and exhaust_dia > 0:
        intake_area = math.pi * (intake_dia/2)**2
        exhaust_area = math.pi * (exhaust_dia/2)**2
        
        # Estimate flow velocities (simplified)
        typical_mass_flow = 0.1  # kg/s assumption
        air_density = 1.2  # kg/m³
        
        intake_velocity = typical_mass_flow / (air_density * intake_area / 10000)  # m/s
        exhaust_velocity = typical_mass_flow / (air_density * exhaust_area / 10000)  # m/s
        
        if intake_velocity > 100:
            result.add_error(f"Estimated intake velocity ({intake_velocity:.0f} m/s) is high - may cause choking", 
                            ValidationCategory.WARNING)
        
        if exhaust_velocity > 300:
            result.add_error(f"Estimated exhaust velocity ({exhaust_velocity:.0f} m/s) may approach sonic conditions", 
                            ValidationCategory.INFO)


# Valve System Validation Functions
def validate_valve_parameters(valve_type: str, num_valves: int, valve_area: float,
                            intake_area: float, validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Tuple[bool, List[str]]:
    """
    Validate valve system parameters
    
    Args:
        valve_type (str): Type of valves
        num_valves (int): Number of valves
        valve_area (float): Total valve area (cm²)
        intake_area (float): Intake cross-sectional area (cm²)
        validation_level (ValidationLevel): Strictness of validation
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    result = ValidationResult(True, [], [], [])
    limits = ValidationLimits.VALVE_LIMITS[validation_level]
    
    # Validate valve type
    valid_valve_types = ["Reed Valves", "Flapper Valves", "Rotary Valves"]
    if valve_type not in valid_valve_types:
        result.add_error(f"Valve type must be one of: {', '.join(valid_valve_types)}")
    
    # Basic range validation
    _validate_parameter_range(result, "Number of valves", num_valves, 
                            limits['num_valves'], "", int)
    _validate_parameter_range(result, "Valve area", valve_area, 
                            limits['valve_area'], "cm²")
    
    # Valve area consistency
    if valve_area <= 0:
        result.add_error("Valve area must be positive")
    elif num_valves > 0:
        area_per_valve = valve_area / num_valves
        if area_per_valve < 1:
            result.add_error(f"Area per valve ({area_per_valve:.2f} cm²) is very small - may be impractical")
        elif area_per_valve > 20:
            result.add_error(f"Area per valve ({area_per_valve:.1f} cm²) is very large - may cause structural issues", 
                            ValidationCategory.WARNING)
    
    # Valve area to intake area ratio
    if intake_area > 0:
        valve_to_intake_ratio = valve_area / intake_area
        ratio_min, ratio_max = limits['valve_to_intake_ratio']
        
        if valve_to_intake_ratio < ratio_min:
            result.add_error(f"Valve area ({valve_area:.1f} cm²) is small relative to intake area ({intake_area:.1f} cm²) - may restrict breathing")
        elif valve_to_intake_ratio > ratio_max:
            result.add_error(f"Valve area ({valve_area:.1f} cm²) is large relative to intake area ({intake_area:.1f} cm²) - check design", 
                            ValidationCategory.WARNING)
    
    # Valve type specific validation
    _validate_valve_type_compatibility(result, valve_type, num_valves, valve_area, validation_level)
    
    return result.is_valid, result.errors + result.warnings


def _validate_valve_type_compatibility(result: ValidationResult, valve_type: str, 
                                     num_valves: int, valve_area: float,
                                     validation_level: ValidationLevel):
    """Validate valve type specific constraints"""
    
    if valve_type == "Reed Valves":
        if num_valves > 12:
            result.add_error("Reed valve designs typically use 12 or fewer valves", ValidationCategory.WARNING)
        if num_valves < 2:
            result.add_error("Reed valve engines typically need at least 2 valves for reliability", ValidationCategory.INFO)
        
        # Reed valve area constraints
        if valve_area / num_valves > 15:
            result.add_error("Individual reed valves larger than 15 cm² may have flutter issues", ValidationCategory.WARNING)
    
    elif valve_type == "Flapper Valves":
        if num_valves > 6:
            result.add_error("Flapper valve designs typically use 6 or fewer valves", ValidationCategory.WARNING)
        if valve_area / num_valves < 5:
            result.add_error("Flapper valves typically need larger individual areas (>5 cm²)", ValidationCategory.INFO)
    
    elif valve_type == "Rotary Valves":
        if num_valves > 2:
            result.add_error("Rotary valve designs typically use 1-2 valves", ValidationCategory.WARNING)
        if num_valves > 1:
            result.add_error("Multiple rotary valves require complex synchronization", ValidationCategory.INFO)


# Operating Conditions Validation Functions
def validate_operating_conditions(fuel_type: str, air_fuel_ratio: float,
                                ambient_pressure: float, ambient_temp: float,
                                validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Tuple[bool, List[str]]:
    """
    Validate operating condition parameters
    
    Args:
        fuel_type (str): Type of fuel
        air_fuel_ratio (float): Air-to-fuel mass ratio
        ambient_pressure (float): Ambient pressure (kPa)
        ambient_temp (float): Ambient temperature (°C)
        validation_level (ValidationLevel): Strictness of validation
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    result = ValidationResult(True, [], [], [])
    limits = ValidationLimits.OPERATING_LIMITS[validation_level]
    
    # Validate fuel type
    valid_fuels = ["Gasoline", "Propane", "Hydrogen", "Kerosene"]
    if fuel_type not in valid_fuels:
        result.add_error(f"Fuel type must be one of: {', '.join(valid_fuels)}")
    
    # Basic range validation
    _validate_parameter_range(result, "Ambient pressure", ambient_pressure, 
                            limits['ambient_pressure'], "kPa")
    _validate_parameter_range(result, "Ambient temperature", ambient_temp, 
                            limits['ambient_temp'], "°C")
    
    # Air-fuel ratio validation
    if air_fuel_ratio <= 0:
        result.add_error("Air-fuel ratio must be positive")
    else:
        _validate_fuel_air_ratio(result, fuel_type, air_fuel_ratio, validation_level)
    
    # Environmental condition validation
    _validate_environmental_conditions(result, ambient_pressure, ambient_temp, validation_level)
    
    return result.is_valid, result.errors + result.warnings


def _validate_fuel_air_ratio(result: ValidationResult, fuel_type: str, air_fuel_ratio: float,
                           validation_level: ValidationLevel):
    """Validate air-fuel ratio for specific fuel type"""
    
    # Stoichiometric ratios for different fuels
    stoichiometric_ratios = {
        "Gasoline": 14.7,
        "Propane": 15.7,
        "Hydrogen": 34.3,
        "Kerosene": 15.0
    }
    
    if fuel_type not in stoichiometric_ratios:
        return
    
    stoich_ratio = stoichiometric_ratios[fuel_type]
    tolerance = ValidationLimits.OPERATING_LIMITS[validation_level]['air_fuel_ratio_tolerance']
    
    # Calculate deviation from stoichiometric
    deviation = abs(air_fuel_ratio - stoich_ratio) / stoich_ratio
    
    if deviation > tolerance:
        if air_fuel_ratio < stoich_ratio * (1 - tolerance):
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is very rich for {fuel_type} (stoichiometric: {stoich_ratio:.1f}) - may cause incomplete combustion")
        else:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is very lean for {fuel_type} (stoichiometric: {stoich_ratio:.1f}) - may cause misfire")
    elif deviation > tolerance * 0.5:
        if air_fuel_ratio < stoich_ratio:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is rich - will reduce efficiency", ValidationCategory.WARNING)
        else:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is lean - may reduce power", ValidationCategory.WARNING)
    
    # Combustion limits
    if fuel_type == "Gasoline":
        if air_fuel_ratio < 8 or air_fuel_ratio > 25:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is outside combustible limits for gasoline (8-25)")
    elif fuel_type == "Propane":
        if air_fuel_ratio < 10 or air_fuel_ratio > 30:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is outside combustible limits for propane (10-30)")
    elif fuel_type == "Hydrogen":
        if air_fuel_ratio < 15 or air_fuel_ratio > 100:
            result.add_error(f"Air-fuel ratio ({air_fuel_ratio:.1f}) is outside combustible limits for hydrogen (15-100)")


def _validate_environmental_conditions(result: ValidationResult, pressure: float, temperature: float,
                                     validation_level: ValidationLevel):
    """Validate environmental operating conditions"""
    
    # Pressure altitude effects
    if pressure < 85:
        altitude_estimate = (101.325 - pressure) * 8.5  # Rough altitude estimate in km
        result.add_error(f"Low pressure ({pressure:.1f} kPa) indicates high altitude (~{altitude_estimate:.1f} km) - performance will be reduced", 
                        ValidationCategory.WARNING)
    elif pressure > 115:
        result.add_error(f"High pressure ({pressure:.1f} kPa) - ensure sea level or below sea level operation", 
                        ValidationCategory.INFO)
    
    # Temperature effects
    if temperature < -10:
        result.add_error(f"Low temperature ({temperature:.0f}°C) may cause starting difficulties and affect fuel atomization", 
                        ValidationCategory.WARNING)
    elif temperature > 45:
        result.add_error(f"High temperature ({temperature:.0f}°C) may reduce air density and affect performance", 
                        ValidationCategory.WARNING)
    
    # Combined effects
    air_density_ratio = (pressure / 101.325) * (288.15 / (temperature + 273.15))
    if air_density_ratio < 0.8:
        result.add_error(f"Low air density (ratio: {air_density_ratio:.2f}) will significantly reduce performance", 
                        ValidationCategory.WARNING)


# Comprehensive Validation Functions
def validate_all_parameters(geometry_params: Dict, valve_params: Dict, 
                          operating_params: Dict, 
                          validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Tuple[bool, List[str]]:
    """
    Validate all input parameters and return consolidated results
    
    Args:
        geometry_params (dict): Engine geometry parameters
        valve_params (dict): Valve system parameters
        operating_params (dict): Operating condition parameters
        validation_level (ValidationLevel): Strictness of validation
        
    Returns:
        tuple: (is_valid, list_of_all_errors)
    """
    all_errors = []
    overall_valid = True
    
    # Sanitize inputs first
    geometry_params = {k: sanitize_input(v, "float") for k, v in geometry_params.items()}
    valve_params = {k: sanitize_input(v, "float" if k != "valve_type" else "str") for k, v in valve_params.items()}
    operating_params = {k: sanitize_input(v, "float" if k != "fuel_type" else "str") for k, v in operating_params.items()}
    
    # Validate geometry
    geom_valid, geom_errors = validate_geometry_parameters(
        geometry_params['combustion_chamber_length'],
        geometry_params['combustion_chamber_diameter'],
        geometry_params['intake_diameter'],
        geometry_params['exhaust_diameter'],
        geometry_params['exhaust_length'],
        validation_level
    )
    if not geom_valid:
        all_errors.extend([f"Geometry: {error}" for error in geom_errors])
        overall_valid = False
    
    # Calculate intake area for valve validation
    intake_area = math.pi * (geometry_params['intake_diameter']/2)**2
    
    # Validate valves
    valve_valid, valve_errors = validate_valve_parameters(
        valve_params['valve_type'],
        int(valve_params['num_valves']),
        valve_params['valve_area'],
        intake_area,
        validation_level
    )
    if not valve_valid:
        all_errors.extend([f"Valves: {error}" for error in valve_errors])
        overall_valid = False
    
    # Validate operating conditions
    op_valid, op_errors = validate_operating_conditions(
        operating_params['fuel_type'],
        operating_params['air_fuel_ratio'],
        operating_params['ambient_pressure'],
        operating_params['ambient_temp'],
        validation_level
    )
    if not op_valid:
        all_errors.extend([f"Operating: {error}" for error in op_errors])
        overall_valid = False
    
    # Cross-parameter validation
    cross_valid, cross_errors = validate_cross_parameter_consistency(
        geometry_params, valve_params, operating_params, validation_level
    )
    if not cross_valid:
        all_errors.extend([f"System: {error}" for error in cross_errors])
        overall_valid = False
    
    return overall_valid, all_errors


def validate_cross_parameter_consistency(geometry_params: Dict, valve_params: Dict,
                                       operating_params: Dict, 
                                       validation_level: ValidationLevel) -> Tuple[bool, List[str]]:
    """
    Validate consistency between different parameter groups
    
    Args:
        geometry_params (dict): Geometry parameters
        valve_params (dict): Valve parameters
        operating_params (dict): Operating parameters
        validation_level (ValidationLevel): Validation strictness
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    result = ValidationResult(True, [], [], [])
    
    # Calculate key derived parameters
    chamber_volume = (math.pi * (geometry_params['combustion_chamber_diameter']/2)**2 * 
                     geometry_params['combustion_chamber_length'] / 1000)  # L
    intake_area = math.pi * (geometry_params['intake_diameter']/2)**2  # cm²
    
    # Engine size vs valve configuration consistency
    if chamber_volume < 0.5 and valve_params['num_valves'] > 6:
        result.add_error("Too many valves for small engine size - may cause packaging issues", 
                        ValidationCategory.WARNING)
    elif chamber_volume > 10 and valve_params['num_valves'] < 4:
        result.add_error("Too few valves for large engine size - may restrict breathing", 
                        ValidationCategory.WARNING)
    
    # Fuel type vs engine size consistency
    fuel_type = operating_params['fuel_type']
    if fuel_type == "Hydrogen":
        if chamber_volume > 5:
            result.add_error("Large combustion volume with hydrogen may pose safety risks", 
                            ValidationCategory.WARNING)
        if valve_params['valve_type'] == "Reed Valves":
            result.add_error("Reed valves with hydrogen may have durability concerns", 
                            ValidationCategory.INFO)
    
    # Operating conditions vs geometry consistency
    temp = operating_params['ambient_temp']
    if temp < 0 and geometry_params['exhaust_length'] > 150:
        result.add_error("Long exhaust length in cold conditions may cause condensation issues", 
                        ValidationCategory.INFO)
    
    # Estimate performance feasibility
    _validate_performance_feasibility(result, geometry_params, valve_params, operating_params)
    
    return result.is_valid, result.errors + result.warnings


def _validate_performance_feasibility(result: ValidationResult, geometry_params: Dict, 
                                    valve_params: Dict, operating_params: Dict):
    """Validate if the configuration is likely to produce reasonable performance"""
    
    # Very rough performance estimates for feasibility check
    chamber_volume = (math.pi * (geometry_params['combustion_chamber_diameter']/2)**2 * 
                     geometry_params['combustion_chamber_length'] / 1000)  # L
    
    # Estimate frequency (very simplified)
    estimated_freq = 15000 / math.sqrt(geometry_params['exhaust_length'] * 
                                      (geometry_params['combustion_chamber_length'] + 
                                       geometry_params['exhaust_length']/3))
    
    if estimated_freq < 10:
        result.add_error("Estimated frequency is very low - engine may not operate properly", 
                        ValidationCategory.WARNING)
    elif estimated_freq > 500:
        result.add_error("Estimated frequency is very high - may cause structural issues", 
                        ValidationCategory.WARNING)
    
    # Estimate thrust-to-volume ratio
    estimated_thrust_per_liter = chamber_volume * 20  # Very rough estimate
    if estimated_thrust_per_liter < 5:
        result.add_error("Configuration may produce very low thrust", ValidationCategory.INFO)
    
    # Check for obvious design issues
    ld_ratio = (geometry_params['combustion_chamber_length'] / 
                geometry_params['combustion_chamber_diameter'])
    area_ratio = ((geometry_params['exhaust_diameter']/2)**2 / 
                  (geometry_params['intake_diameter']/2)**2)
    
    if ld_ratio > 6 and area_ratio < 1.2:
        result.add_error("Long chamber with small exhaust may cause poor scavenging", 
                        ValidationCategory.WARNING)


# Safety and Manufacturing Validation
def validate_design_safety(geometry_params: Dict, valve_params: Dict, 
                         operating_params: Dict) -> Tuple[bool, List[str]]:
    """
    Validate design for safety considerations
    
    Args:
        geometry_params (dict): Geometry parameters
        valve_params (dict): Valve parameters  
        operating_params (dict): Operating parameters
        
    Returns:
        tuple: (is_safe, list_of_safety_concerns)
    """
    result = ValidationResult(True, [], [], [])
    
    # Fuel safety checks
    fuel_type = operating_params['fuel_type']
    chamber_volume = (math.pi * (geometry_params['combustion_chamber_diameter']/2)**2 * 
                     geometry_params['combustion_chamber_length'] / 1000)
    
    if fuel_type == "Hydrogen":
        if chamber_volume > 2:
            result.add_error("Large hydrogen engine poses explosion risk - consider safety measures", 
                            ValidationCategory.CRITICAL)
        result.add_error("Hydrogen fuel requires special handling and ventilation", 
                        ValidationCategory.WARNING)
    
    if fuel_type in ["Gasoline", "Kerosene"]:
        if chamber_volume > 20:
            result.add_error("Very large combustion volume poses fire risk", 
                            ValidationCategory.WARNING)
    
    # Pressure safety
    if operating_params['ambient_pressure'] > 110:
        result.add_error("High pressure operation may exceed design limits", 
                        ValidationCategory.WARNING)
    
    # Temperature safety  
    if operating_params['ambient_temp'] > 50:
        result.add_error("High temperature operation may cause overheating", 
                        ValidationCategory.WARNING)
    
    # Structural safety estimates
    estimated_freq = 15000 / math.sqrt(geometry_params['exhaust_length'] * 
                                      geometry_params['combustion_chamber_length'])
    
    if estimated_freq > 300:
        result.add_error("High frequency operation may cause fatigue failure", 
                        ValidationCategory.CRITICAL)
    
    # Exhaust safety
    if geometry_params['exhaust_length'] > 200:
        result.add_error("Very long exhaust may pose mounting and vibration challenges", 
                        ValidationCategory.WARNING)
    
    return result.is_valid, result.errors + result.warnings


def validate_manufacturing_feasibility(geometry_params: Dict, valve_params: Dict) -> Tuple[bool, List[str]]:
    """
    Validate design for manufacturing feasibility
    
    Args:
        geometry_params (dict): Geometry parameters
        valve_params (dict): Valve parameters
        
    Returns:
        tuple: (is_manufacturable, list_of_manufacturing_concerns)
    """
    result = ValidationResult(True, [], [], [])
    
    # Minimum feature sizes
    min_diameter = min(geometry_params['intake_diameter'], geometry_params['exhaust_diameter'])
    if min_diameter < 5:
        result.add_error("Very small diameters may be difficult to machine accurately", 
                        ValidationCategory.WARNING)
    
    # Wall thickness estimates
    chamber_diameter = geometry_params['combustion_chamber_diameter']
    if chamber_diameter > 30:
        result.add_error("Large diameter chambers require thick walls - consider weight impact", 
                        ValidationCategory.INFO)
    
    # Aspect ratio manufacturability
    chamber_length = geometry_params['combustion_chamber_length']
    if chamber_length / chamber_diameter > 8:
        result.add_error("High aspect ratio chambers are difficult to machine", 
                        ValidationCategory.WARNING)
    
    # Valve manufacturing
    if valve_params['num_valves'] > 10:
        result.add_error("Many valves increase manufacturing complexity and cost", 
                        ValidationCategory.INFO)
    
    individual_valve_area = valve_params['valve_area'] / valve_params['num_valves']
    if individual_valve_area < 2:
        result.add_error("Very small individual valves may be difficult to manufacture", 
                        ValidationCategory.WARNING)
    elif individual_valve_area > 25:
        result.add_error("Very large individual valves may have structural challenges", 
                        ValidationCategory.WARNING)
    
    # Tolerance considerations
    diameter_tolerance = chamber_diameter * 0.01  # 1% tolerance
    if diameter_tolerance < 0.1:
        result.add_error("Tight tolerances required - may increase manufacturing cost", 
                        ValidationCategory.INFO)
    
    return result.is_valid, result.errors + result.warnings


# UI Integration Functions
def show_validation_results(is_valid: bool, errors: List[str], warnings: List[str] = None):
    """
    Display validation results in Streamlit UI
    
    Args:
        is_valid (bool): Whether validation passed
        errors (list): List of error messages
        warnings (list, optional): List of warning messages
    """
    if not STREAMLIT_AVAILABLE:
        # Fallback for non-Streamlit environments
        if is_valid:
            print("✅ All parameters are valid")
        else:
            print("❌ Parameter validation failed:")
            for error in errors:
                print(f"  • {error}")
        return
    
    if is_valid:
        st.success("✅ All parameters are valid")
    else:
        st.error("❌ Parameter validation failed:")
        for error in errors:
            st.error(f"• {error}")
    
    # Show warnings if provided
    if warnings:
        for warning in warnings:
            st.warning(f"⚠️ {warning}")


def create_validation_summary(geometry_params: Dict, valve_params: Dict, 
                            operating_params: Dict) -> str:
    """
    Create a comprehensive validation summary report
    
    Args:
        geometry_params (dict): Geometry parameters
        valve_params (dict): Valve parameters
        operating_params (dict): Operating parameters
        
    Returns:
        str: Validation summary report
    """
    summary = "# Parameter Validation Summary\n\n"
    
    # Run all validations
    all_valid, all_errors = validate_all_parameters(geometry_params, valve_params, operating_params)
    safety_valid, safety_errors = validate_design_safety(geometry_params, valve_params, operating_params)
    mfg_valid, mfg_errors = validate_manufacturing_feasibility(geometry_params, valve_params)
    
    # Overall status
    if all_valid and safety_valid and mfg_valid:
        summary += "## ✅ Overall Status: PASSED\n\n"
        summary += "All parameters pass validation checks.\n\n"
    else:
        summary += "## ❌ Overall Status: ISSUES FOUND\n\n"
    
    # Detailed results
    if not all_valid:
        summary += "### Parameter Validation Issues\n"
        for error in all_errors:
            summary += f"- {error}\n"
        summary += "\n"
    
    if not safety_valid:
        summary += "### Safety Concerns\n"
        for error in safety_errors:
            summary += f"- {error}\n"
        summary += "\n"
    
    if not mfg_valid:
        summary += "### Manufacturing Considerations\n"
        for error in mfg_errors:
            summary += f"- {error}\n"
        summary += "\n"
    
    # Recommendations
    summary += "### Recommendations\n"
    if all_valid and safety_valid and mfg_valid:
        summary += "- Proceed with detailed analysis\n"
        summary += "- Consider prototype development\n"
    else:
        summary += "- Address validation issues before proceeding\n"
        summary += "- Consider design modifications\n"
        summary += "- Consult with engineering experts\n"
    
    summary += f"\n*Validation performed at {ValidationLevel.NORMAL.value} level*\n"
    summary += f"*Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return summary


# Utility Functions
def _validate_parameter_range(result: ValidationResult, param_name: str, value: float, 
                            limits: Tuple[float, float], units: str, param_type=float):
    """Helper function to validate parameter ranges"""
    try:
        if param_type == int:
            value = int(value)
        else:
            value = float(value)
            
        min_val, max_val = limits
        
        if value < min_val:
            result.add_error(f"{param_name} ({value}{' ' + units if units else ''}) is below minimum ({min_val}{' ' + units if units else ''})")
        elif value > max_val:
            result.add_error(f"{param_name} ({value}{' ' + units if units else ''}) is above maximum ({max_val}{' ' + units if units else ''})")
            
    except (ValueError, TypeError):
        result.add_error(f"{param_name} must be a valid number")


def sanitize_input(value: Any, param_type: str = "float") -> Union[float, int, str]:
    """
    Sanitize user input to prevent errors
    
    Args:
        value (Any): Input value to sanitize
        param_type (str): Target type ("float", "int", "str")
        
    Returns:
        Union[float, int, str]: Sanitized value
    """
    try:
        if value is None:
            return 0.0 if param_type == "float" else (0 if param_type == "int" else "")
        
        if param_type == "float":
            # Handle string inputs that might have units or other text
            if isinstance(value, str):
                # Extract numeric part using regex
                import re
                numeric_match = re.search(r'[-+]?(\d+\.?\d*|\.\d+)', value)
                if numeric_match:
                    return float(numeric_match.group())
                else:
                    return 0.0
            return float(value)
            
        elif param_type == "int":
            if isinstance(value, str):
                import re
                numeric_match = re.search(r'[-+]?\d+', value)
                if numeric_match:
                    return int(numeric_match.group())
                else:
                    return 0
            return int(float(value))  # Convert through float to handle decimals
            
        elif param_type == "str":
            return str(value) if value is not None else ""
            
        else:
            return value
            
    except (ValueError, TypeError, AttributeError):
        # Return safe defaults
        if param_type == "float":
            return 0.0
        elif param_type == "int":
            return 0
        else:
            return ""


def get_validation_limits(validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Dict:
    """
    Get validation limits for a specific level
    
    Args:
        validation_level (ValidationLevel): Validation strictness level
        
    Returns:
        dict: Complete validation limits
    """
    return {
        'geometry': ValidationLimits.GEOMETRY_LIMITS[validation_level],
        'valves': ValidationLimits.VALVE_LIMITS[validation_level],
        'operating': ValidationLimits.OPERATING_LIMITS[validation_level]
    }


def validate_single_parameter(param_name: str, value: float, param_category: str,
                             validation_level: ValidationLevel = ValidationLevel.NORMAL) -> Tuple[bool, str]:
    """
    Validate a single parameter
    
    Args:
        param_name (str): Name of parameter
        value (float): Parameter value
        param_category (str): Category ("geometry", "valves", "operating")
        validation_level (ValidationLevel): Validation level
        
    Returns:
        tuple: (is_valid, error_message)
    """
    limits = get_validation_limits(validation_level)
    
    if param_category not in limits:
        return False, f"Unknown parameter category: {param_category}"
    
    category_limits = limits[param_category]
    
    if param_name not in category_limits:
        return True, ""  # No specific limits defined
    
    min_val, max_val = category_limits[param_name]
    
    if value < min_val:
        return False, f"{param_name} ({value}) is below minimum ({min_val})"
    elif value > max_val:
        return False, f"{param_name} ({value}) is above maximum ({max_val})"
    else:
        return True, ""


# Export all public functions
__all__ = [
    # Enums
    'ValidationLevel',
    'ValidationCategory',
    'ValidationResult',
    
    # Main validation functions
    'validate_geometry_parameters',
    'validate_valve_parameters', 
    'validate_operating_conditions',
    'validate_all_parameters',
    
    # Specialized validation
    'validate_design_safety',
    'validate_manufacturing_feasibility',
    'validate_cross_parameter_consistency',
    
    # UI integration
    'show_validation_results',
    'create_validation_summary',
    
    # Utilities
    'sanitize_input',
    'get_validation_limits',
    'validate_single_parameter',
    
    # Constants
    'ValidationLimits'
]
