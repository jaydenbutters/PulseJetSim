# src/__init__.py
"""
Pulse Jet Engine Design & Performance Modeler

A comprehensive tool for modeling and analyzing pulse jet engine designs.
This package provides physics-based models for performance prediction,
optimization tools, and validation utilities.

Features:
- Physics-based pulse jet performance modeling
- Interactive Streamlit web interface
- Parameter optimization and sensitivity analysis
- Design validation and recommendations
- Configuration management and data export
- Multi-fuel support with real properties

Modules:
- pulse_jet_models: Core physics models and calculations
- utils: Utility functions for data handling and export
- validators: Input validation and error checking

Example:
    Basic usage of the pulse jet modeler:
    
    >>> from src.pulse_jet_models import PulseJetModel, EngineGeometry
    >>> from src.pulse_jet_models import ValveSystem, OperatingConditions
    >>> 
    >>> # Create model instance
    >>> model = PulseJetModel()
    >>> 
    >>> # Define engine geometry
    >>> geometry = EngineGeometry(
    ...     combustion_chamber_length=50,
    ...     combustion_chamber_diameter=15,
    ...     intake_diameter=8,
    ...     exhaust_diameter=10,
    ...     exhaust_length=80
    ... )
    >>> 
    >>> # Define valve system
    >>> valves = ValveSystem(
    ...     valve_type="Reed Valves",
    ...     num_valves=4,
    ...     valve_area=20
    ... )
    >>> 
    >>> # Define operating conditions
    >>> conditions = OperatingConditions(
    ...     fuel_type="Gasoline",
    ...     air_fuel_ratio=14.7,
    ...     ambient_pressure=101.3,
    ...     ambient_temp=20
    ... )
    >>> 
    >>> # Run analysis
    >>> results = model.run_complete_analysis(geometry, valves, conditions)
    >>> print(f"Thrust: {results.thrust:.1f} N")
    >>> print(f"Frequency: {results.frequency:.0f} Hz")

Author: Pulse Jet Modeler Contributors
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Pulse Jet Modeler Contributors"
__email__ = "contributors@pulse-jet-modeler.org"
__license__ = "MIT"
__copyright__ = "2024 Pulse Jet Modeler Contributors"
__status__ = "Beta"
__maintainer__ = "Pulse Jet Modeler Team"
__url__ = "https://github.com/your-username/pulse-jet-modeler"
__description__ = "A comprehensive tool for pulse jet engine design and performance modeling"

# Import main classes and functions for easy access
from .pulse_jet_models import (
    PulseJetModel,
    EngineGeometry,
    ValveSystem,
    OperatingConditions,
    PerformanceResults,
    OptimizationAnalyzer
)

from .utils import (
    load_config,
    load_fuel_properties,
    save_configuration,
    load_configuration,
    export_results_to_csv,
    format_parameter_value,
    calculate_design_score,
    generate_design_report,
    create_comparison_table
)

from .validators import (
    validate_geometry_parameters,
    validate_valve_parameters,
    validate_operating_conditions,
    validate_all_parameters,
    show_validation_results,
    sanitize_input
)

# Define what gets imported with "from src import *"
__all__ = [
    # Core model classes
    'PulseJetModel',
    'EngineGeometry', 
    'ValveSystem',
    'OperatingConditions',
    'PerformanceResults',
    'OptimizationAnalyzer',
    
    # Utility functions
    'load_config',
    'load_fuel_properties',
    'save_configuration',
    'load_configuration',
    'export_results_to_csv',
    'format_parameter_value',
    'calculate_design_score',
    'generate_design_report',
    'create_comparison_table',
    
    # Validation functions
    'validate_geometry_parameters',
    'validate_valve_parameters', 
    'validate_operating_conditions',
    'validate_all_parameters',
    'show_validation_results',
    'sanitize_input',
    
    # Package metadata
    '__version__',
    '__author__',
    '__license__',
    '__description__'
]

# Package-level constants
DEFAULT_CONFIG_FILE = "config.yaml"
DEFAULT_FUEL_PROPERTIES_FILE = "data/fuel_properties.json"
DEFAULT_SAMPLE_CONFIGS_FILE = "data/sample_configurations.json"

# Supported fuel types
SUPPORTED_FUELS = ["Gasoline", "Propane", "Hydrogen", "Kerosene"]

# Supported valve types
SUPPORTED_VALVE_TYPES = ["Reed Valves", "Flapper Valves", "Rotary Valves"]

# Physical constants used throughout the package
PHYSICAL_CONSTANTS = {
    'R_air': 287,  # Specific gas constant for air (J/kg·K)
    'gamma': 1.4,  # Heat capacity ratio for air
    'g': 9.81,     # Standard gravity (m/s²)
    'std_pressure': 101325,  # Standard atmospheric pressure (Pa)
    'std_temperature': 288.15,  # Standard temperature (K)
}

# Model default parameters
MODEL_DEFAULTS = {
    'combustion_efficiency': 0.85,
    'valve_discharge_coefficient': 0.8,
    'exhaust_efficiency': 0.95,
    'frequency_constant': 17000
}

def get_version_info():
    """
    Get detailed version information
    
    Returns:
        dict: Dictionary containing version information
    """
    return {
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'status': __status__,
        'python_requires': '>=3.8',
        'homepage': __url__
    }

def check_dependencies():
    """
    Check if all required dependencies are available
    
    Returns:
        dict: Dictionary with dependency status
    """
    dependencies = {
        'streamlit': False,
        'numpy': False,
        'pandas': False,
        'plotly': False,
        'pyyaml': False,
        'scipy': False
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
    
    return dependencies

def print_package_info():
    """Print package information"""
    print(f"Pulse Jet Modeler v{__version__}")
    print(f"Author: {__author__}")
    print(f"License: {__license__}")
    print(f"Homepage: {__url__}")
    print(f"Description: {__description__}")
    
    # Check dependencies
    deps = check_dependencies()
    print("\nDependency Status:")
    for dep, status in deps.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {dep}")

# Convenience function for quick model creation
def create_default_model():
    """
    Create a PulseJetModel instance with default settings
    
    Returns:
        PulseJetModel: Configured model instance
    """
    return PulseJetModel()

def create_sample_engine(engine_type="medium"):
    """
    Create sample engine configurations
    
    Args:
        engine_type (str): Type of engine ("small", "medium", "large")
        
    Returns:
        tuple: (EngineGeometry, ValveSystem, OperatingConditions)
    """
    if engine_type == "small":
        geometry = EngineGeometry(
            combustion_chamber_length=30,
            combustion_chamber_diameter=8,
            intake_diameter=4,
            exhaust_diameter=5,
            exhaust_length=40
        )
        valves = ValveSystem(
            valve_type="Reed Valves",
            num_valves=2,
            valve_area=8
        )
    elif engine_type == "large":
        geometry = EngineGeometry(
            combustion_chamber_length=80,
            combustion_chamber_diameter=25,
            intake_diameter=12,
            exhaust_diameter=16,
            exhaust_length=120
        )
        valves = ValveSystem(
            valve_type="Reed Valves",
            num_valves=8,
            valve_area=40
        )
    else:  # medium (default)
        geometry = EngineGeometry(
            combustion_chamber_length=50,
            combustion_chamber_diameter=15,
            intake_diameter=8,
            exhaust_diameter=10,
            exhaust_length=80
        )
        valves = ValveSystem(
            valve_type="Reed Valves",
            num_valves=4,
            valve_area=20
        )
    
    # Standard operating conditions
    conditions = OperatingConditions(
        fuel_type="Gasoline",
        air_fuel_ratio=14.7,
        ambient_pressure=101.3,
        ambient_temp=20
    )
    
    return geometry, valves, conditions

# Package initialization
def _initialize_package():
    """Initialize package on import"""
    import warnings
    
    # Filter specific warnings if needed
    warnings.filterwarnings('ignore', category=UserWarning, module='plotly')
    
    # Check for critical dependencies
    critical_deps = ['numpy', 'pandas', 'streamlit']
    missing_deps = []
    
    for dep in critical_deps:
        try:
            __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        raise ImportError(
            f"Missing critical dependencies: {', '.join(missing_deps)}. "
            f"Please install them using: pip install {' '.join(missing_deps)}"
        )

# Run initialization
_initialize_package()

---

# tests/__init__.py
"""
Test package for Pulse Jet Engine Design & Performance Modeler

This package contains unit tests, integration tests, and test utilities
for validating the pulse jet modeling functionality.

Test Structure:
- test_models.py: Tests for core physics models
- test_utils.py: Tests for utility functions
- test_validators.py: Tests for input validation
- test_integration.py: End-to-end integration tests

Usage:
    Run all tests:
    >>> pytest tests/
    
    Run specific test file:
    >>> pytest tests/test_models.py
    
    Run with coverage:
    >>> pytest tests/ --cov=src --cov-report=html

Test Data:
The tests use predefined test cases and sample data to ensure
consistent and reproducible results across different environments.
"""

__version__ = "1.0.0"

import sys
import os
from pathlib import Path

# Add src directory to path for imports during testing
TEST_DIR = Path(__file__).parent
PROJECT_ROOT = TEST_DIR.parent
SRC_DIR = PROJECT_ROOT / 'src'

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Test configuration
TEST_CONFIG = {
    'tolerance': {
        'geometry': 1e-6,      # Tolerance for geometry calculations
        'frequency': 1e-2,     # Tolerance for frequency calculations (Hz)
        'mass_flow': 1e-6,     # Tolerance for mass flow calculations (kg/s)
        'thrust': 1e-3,        # Tolerance for thrust calculations (N)
        'efficiency': 1e-3,    # Tolerance for efficiency calculations (%)
    },
    'test_data_dir': TEST_DIR / 'data',
    'temp_dir': TEST_DIR / 'temp',
    'fixtures_dir': TEST_DIR / 'fixtures'
}

# Sample test geometries for consistent testing
SAMPLE_GEOMETRIES = {
    'small': {
        'combustion_chamber_length': 30,
        'combustion_chamber_diameter': 8,
        'intake_diameter': 4,
        'exhaust_diameter': 5,
        'exhaust_length': 40
    },
    'medium': {
        'combustion_chamber_length': 50,
        'combustion_chamber_diameter': 15,
        'intake_diameter': 8,
        'exhaust_diameter': 10,
        'exhaust_length': 80
    },
    'large': {
        'combustion_chamber_length': 80,
        'combustion_chamber_diameter': 25,
        'intake_diameter': 12,
        'exhaust_diameter': 16,
        'exhaust_length': 120
    }
}

# Sample valve configurations
SAMPLE_VALVES = {
    'reed_small': {
        'valve_type': 'Reed Valves',
        'num_valves': 2,
        'valve_area': 8
    },
    'reed_medium': {
        'valve_type': 'Reed Valves',
        'num_valves': 4,
        'valve_area': 20
    },
    'flapper_medium': {
        'valve_type': 'Flapper Valves',
        'num_valves': 3,
        'valve_area': 18
    }
}

# Sample operating conditions
SAMPLE_CONDITIONS = {
    'standard': {
        'fuel_type': 'Gasoline',
        'air_fuel_ratio': 14.7,
        'ambient_pressure': 101.3,
        'ambient_temp': 20
    },
    'cold': {
        'fuel_type': 'Gasoline',
        'air_fuel_ratio': 14.7,
        'ambient_pressure': 101.3,
        'ambient_temp': -10
    },
    'hot': {
        'fuel_type': 'Gasoline',
        'air_fuel_ratio': 14.7,
        'ambient_pressure': 101.3,
        'ambient_temp': 40
    },
    'hydrogen': {
        'fuel_type': 'Hydrogen',
        'air_fuel_ratio': 34.3,
        'ambient_pressure': 101.3,
        'ambient_temp': 20
    }
}

def setup_test_environment():
    """Set up test environment and directories"""
    # Create test directories if they don't exist
    for dir_path in [TEST_CONFIG['temp_dir'], TEST_CONFIG['fixtures_dir']]:
        dir_path.mkdir(parents=True, exist_ok=True)

def cleanup_test_environment():
    """Clean up test environment"""
    import shutil
    
    # Clean up temporary files
    if TEST_CONFIG['temp_dir'].exists():
        shutil.rmtree(TEST_CONFIG['temp_dir'])

def get_sample_geometry(size='medium'):
    """
    Get sample geometry for testing
    
    Args:
        size (str): Size of engine ('small', 'medium', 'large')
        
    Returns:
        dict: Geometry parameters
    """
    return SAMPLE_GEOMETRIES.get(size, SAMPLE_GEOMETRIES['medium'])

def get_sample_valves(valve_config='reed_medium'):
    """
    Get sample valve configuration for testing
    
    Args:
        valve_config (str): Valve configuration name
        
    Returns:
        dict: Valve parameters
    """
    return SAMPLE_VALVES.get(valve_config, SAMPLE_VALVES['reed_medium'])

def get_sample_conditions(condition_type='standard'):
    """
    Get sample operating conditions for testing
    
    Args:
        condition_type (str): Condition type name
        
    Returns:
        dict: Operating condition parameters
    """
    return SAMPLE_CONDITIONS.get(condition_type, SAMPLE_CONDITIONS['standard'])

# Test utilities
class TestDataGenerator:
    """Generate test data for various test scenarios"""
    
    @staticmethod
    def generate_parameter_range(param_name, num_points=10):
        """Generate parameter ranges for sweep testing"""
        import numpy as np
        
        ranges = {
            'exhaust_length': (20, 200),
            'combustion_chamber_diameter': (5, 30),
            'air_fuel_ratio': (10, 20),
            'ambient_temp': (-20, 50)
        }
        
        if param_name in ranges:
            min_val, max_val = ranges[param_name]
            return np.linspace(min_val, max_val, num_points)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")
    
    @staticmethod
    def generate_test_configurations(num_configs=5):
        """Generate random test configurations"""
        import random
        
        configs = []
        for i in range(num_configs):
            config = {
                'geometry': {
                    'combustion_chamber_length': random.uniform(20, 100),
                    'combustion_chamber_diameter': random.uniform(8, 25),
                    'intake_diameter': random.uniform(4, 15),
                    'exhaust_diameter': random.uniform(5, 20),
                    'exhaust_length': random.uniform(30, 150)
                },
                'valves': {
                    'valve_type': random.choice(['Reed Valves', 'Flapper Valves']),
                    'num_valves': random.randint(2, 8),
                    'valve_area': random.uniform(10, 40)
                },
                'operating': {
                    'fuel_type': random.choice(['Gasoline', 'Propane']),
                    'air_fuel_ratio': random.uniform(12, 18),
                    'ambient_pressure': random.uniform(90, 110),
                    'ambient_temp': random.uniform(0, 40)
                }
            }
            configs.append(config)
        
        return configs

# Initialize test environment on import
setup_test_environment()

---

# data/__init__.py
"""
Data package for Pulse Jet Engine Design & Performance Modeler

This package contains data files and utilities for loading fuel properties,
sample configurations, and other reference data used by the pulse jet modeler.

Data Files:
- fuel_properties.json: Fuel characteristics and properties
- sample_configurations.json: Example engine configurations
- validation_data.json: Reference data for model validation

Usage:
    Load fuel properties:
    >>> from data import load_fuel_data
    >>> fuel_props = load_fuel_data()
    
    Load sample configurations:
    >>> from data import load_sample_configs
    >>> configs = load_sample_configs()
"""

__version__ = "1.0.0"

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Data directory path
DATA_DIR = Path(__file__).parent

def load_fuel_data(filename: str = "fuel_properties.json") -> Dict[str, Dict]:
    """
    Load fuel properties from JSON file
    
    Args:
        filename (str): Name of the fuel properties file
        
    Returns:
        dict: Fuel properties dictionary
    """
    file_path = DATA_DIR / filename
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        # Return default fuel properties if file not found
        return get_default_fuel_properties()
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in fuel properties file: {e}")

def load_sample_configs(filename: str = "sample_configurations.json") -> List[Dict]:
    """
    Load sample configurations from JSON file
    
    Args:
        filename (str): Name of the sample configurations file
        
    Returns:
        list: List of sample configuration dictionaries
    """
    file_path = DATA_DIR / filename
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data.get('configurations', [])
    except FileNotFoundError:
        return get_default_configurations()
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in sample configurations file: {e}")

def get_default_fuel_properties() -> Dict[str, Dict]:
    """Get default fuel properties if file is missing"""
    return {
        "Gasoline": {
            "heating_value": 44.0,
            "density": 0.75,
            "stoich_ratio": 14.7,
            "molecular_weight": 100,
            "autoignition_temp": 280,
            "flash_point": -43,
            "boiling_point": 38
        },
        "Propane": {
            "heating_value": 46.4,
            "density": 0.51,
            "stoich_ratio": 15.7,
            "molecular_weight": 44,
            "autoignition_temp": 470,
            "flash_point": -104,
            "boiling_point": -42
        },
        "Hydrogen": {
            "heating_value": 120.0,
            "density": 0.0899,
            "stoich_ratio": 34.3,
            "molecular_weight": 2,
            "autoignition_temp": 500,
            "flash_point": -253,
            "boiling_point": -253
        },
        "Kerosene": {
            "heating_value": 43.2,
            "density": 0.82,
            "stoich_ratio": 15.0,
            "molecular_weight": 170,
            "autoignition_temp": 210,
            "flash_point": 38,
            "boiling_point": 150
        }
    }

def get_default_configurations() -> List[Dict]:
    """Get default sample configurations if file is missing"""
    return [
        {
            "name": "Small Hobby Engine",
            "description": "Compact design for RC aircraft",
            "geometry": {
                "combustion_chamber_length": 30,
                "combustion_chamber_diameter": 8,
                "intake_diameter": 4,
                "exhaust_diameter": 5,
                "exhaust_length": 40
            },
            "valves": {
                "valve_type": "Reed Valves",
                "num_valves": 2,
                "valve_area": 8
            },
            "operating": {
                "fuel_type": "Gasoline",
                "air_fuel_ratio": 14.7,
                "ambient_pressure": 101.3,
                "ambient_temp": 20
            }
        },
        {
            "name": "Medium Performance Engine",
            "description": "Balanced design for general applications",
            "geometry": {
                "combustion_chamber_length": 50,
                "combustion_chamber_diameter": 15,
                "intake_diameter": 8,
                "exhaust_diameter": 10,
                "exhaust_length": 80
            },
            "valves": {
                "valve_type": "Reed Valves",
                "num_valves": 4,
                "valve_area": 20
            },
            "operating": {
                "fuel_type": "Gasoline",
                "air_fuel_ratio": 14.7,
                "ambient_pressure": 101.3,
                "ambient_temp": 20
            }
        }
    ]

def save_fuel_data(fuel_data: Dict[str, Dict], filename: str = "fuel_properties.json") -> bool:
    """
    Save fuel properties to JSON file
    
    Args:
        fuel_data (dict): Fuel properties to save
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = DATA_DIR / filename
    
    try:
        with open(file_path, 'w') as f:
            json.dump(fuel_data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving fuel data: {e}")
        return False

def save_sample_configs(configs: List[Dict], filename: str = "sample_configurations.json") -> bool:
    """
    Save sample configurations to JSON file
    
    Args:
        configs (list): List of configurations to save
        filename (str): Output filename
        
    Returns:
        bool: True if successful, False otherwise
    """
    file_path = DATA_DIR / filename
    
    try:
        data = {"configurations": configs}
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving sample configurations: {e}")
        return False

def validate_fuel_properties(fuel_data: Dict[str, Dict]) -> bool:
    """
    Validate fuel properties data structure
    
    Args:
        fuel_data (dict): Fuel properties to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = [
        'heating_value', 'density', 'stoich_ratio', 
        'molecular_weight', 'autoignition_temp'
    ]
    
    for fuel_name, properties in fuel_data.items():
        for field in required_fields:
            if field not in properties:
                print(f"Missing field '{field}' for fuel '{fuel_name}'")
                return False
            
            if not isinstance(properties[field], (int, float)):
                print(f"Invalid type for field '{field}' in fuel '{fuel_name}'")
                return False
    
    return True

# Data validation utilities
def get_fuel_property(fuel_type: str, property_name: str, default: Optional[float] = None) -> Optional[float]:
    """
    Get specific fuel property with fallback
    
    Args:
        fuel_type (str): Type of fuel
        property_name (str): Name of property to retrieve
        default (float, optional): Default value if property not found
        
    Returns:
        float or None: Property value or default
    """
    fuel_data = load_fuel_data()
    
    if fuel_type in fuel_data and property_name in fuel_data[fuel_type]:
        return fuel_data[fuel_type][property_name]
    
    return default

def list_available_fuels() -> List[str]:
    """
    Get list of available fuel types
    
    Returns:
        list: List of fuel type names
    """
    fuel_data = load_fuel_data()
    return list(fuel_data.keys())

def list_sample_configurations() -> List[str]:
    """
    Get list of available sample configuration names
    
    Returns:
        list: List of configuration names
    """
    configs = load_sample_configs()
    return [config['name'] for config in configs]

# Package constants
SUPPORTED_FUELS = ["Gasoline", "Propane", "Hydrogen", "Kerosene"]
REQUIRED_FUEL_PROPERTIES = [
    'heating_value', 'density', 'stoich_ratio', 
    'molecular_weight', 'autoignition_temp'
]

__all__ = [
    'load_fuel_data',
    'load_sample_configs', 
    'get_default_fuel_properties',
    'get_default_configurations',
    'save_fuel_data',
    'save_sample_configs',
    'validate_fuel_properties',
    'get_fuel_property',
    'list_available_fuels',
    'list_sample_configurations',
    'SUPPORTED_FUELS',
    'REQUIRED_FUEL_PROPERTIES'
]
