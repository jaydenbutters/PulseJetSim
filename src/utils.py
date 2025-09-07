"""
Utility functions for the pulse jet modeler application

This module provides utility functions for configuration management, data handling,
file I/O, mathematical calculations, and formatting operations used throughout
the pulse jet modeling application.

Functions:
    Configuration Management:
        - load_config: Load YAML configuration files
        - save_configuration: Save design configurations
        - load_configuration: Load saved configurations
    
    Data Handling:
        - load_fuel_properties: Load fuel properties database
        - export_results_to_csv: Export analysis results
        - create_comparison_table: Compare multiple designs
    
    Mathematical Utilities:
        - calculate_design_score: Overall design scoring
        - interpolate_data: Data interpolation utilities
        - unit_conversions: Unit conversion functions
    
    Formatting:
        - format_parameter_value: Format values with units
        - generate_design_report: Create comprehensive reports
        - create_performance_summary: Performance summaries

Example:
    Basic usage:
    
    >>> from utils import load_fuel_properties, calculate_design_score
    >>> 
    >>> # Load fuel data
    >>> fuels = load_fuel_properties()
    >>> print(fuels['Gasoline']['heating_value'])
    >>> 
    >>> # Calculate design score
    >>> performance = {'thrust': 50, 'efficiency': 20, 'frequency': 100}
    >>> score = calculate_design_score(performance)
    >>> print(f"Design score: {score:.1f}/100")

Author: Pulse Jet Modeler Contributors
License: MIT
Version: 1.0.0
"""

import json
import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Union, Optional, Tuple
import warnings
from datetime import datetime
import csv
import io
import math
import re

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


# Configuration Management Functions
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load application configuration from YAML file
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            st.warning(f"Configuration file {config_path} not found. Using defaults.")
            return get_default_config()
        
        with open(config_file, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            
        # Validate configuration structure
        if not isinstance(config, dict):
            raise ValueError("Configuration file must contain a dictionary")
            
        return config
        
    except yaml.YAMLError as e:
        st.error(f"Error parsing YAML configuration: {e}")
        return get_default_config()
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """
    Return default configuration if config file is missing
    
    Returns:
        dict: Default configuration dictionary
    """
    return {
        'app': {
            'title': 'Pulse Jet Engine Design & Performance Modeler',
            'icon': '🚀',
            'layout': 'wide',
            'theme': 'light'
        },
        'parameters': {
            'geometry': {
                'combustion_chamber_length': {'min': 10, 'max': 100, 'default': 50, 'unit': 'cm'},
                'combustion_chamber_diameter': {'min': 5, 'max': 30, 'default': 15, 'unit': 'cm'},
                'intake_diameter': {'min': 2, 'max': 15, 'default': 8, 'unit': 'cm'},
                'exhaust_diameter': {'min': 3, 'max': 20, 'default': 10, 'unit': 'cm'},
                'exhaust_length': {'min': 20, 'max': 200, 'default': 80, 'unit': 'cm'}
            },
            'valves': {
                'types': ['Reed Valves', 'Flapper Valves', 'Rotary Valves'],
                'default_type': 'Reed Valves',
                'num_valves': {'min': 1, 'max': 12, 'default': 4},
                'valve_area': {'min': 5, 'max': 50, 'default': 20, 'unit': 'cm²'}
            },
            'operating': {
                'fuel_types': ['Gasoline', 'Propane', 'Hydrogen', 'Kerosene'],
                'default_fuel': 'Gasoline',
                'air_fuel_ratio': {'min': 10.0, 'max': 20.0, 'default': 14.7, 'step': 0.1},
                'ambient_pressure': {'min': 80, 'max': 120, 'default': 101.3, 'step': 0.1, 'unit': 'kPa'},
                'ambient_temp': {'min': -20, 'max': 50, 'default': 20, 'unit': '°C'}
            }
        },
        'model': {
            'constants': {
                'gas_constant': 287,
                'gamma': 1.4,
                'gravity': 9.81,
                'frequency_constant': 17000,
                'efficiency': 0.3,
                'valve_discharge_coeff': 0.8
            }
        },
        'visualization': {
            'colors': {
                'primary': '#FF4B4B',
                'secondary': '#00D4AA',
                'accent': '#FFC107'
            },
            'plot_settings': {
                'dpi': 300,
                'figure_size': [10, 6],
                'grid': True
            }
        },
        'paths': {
            'data': 'data/',
            'exports': 'exports/',
            'configs': 'saved_configs/'
        }
    }


def save_configuration(config_data: Dict[str, Any], filename: str, 
                      directory: str = "saved_configs") -> bool:
    """
    Save configuration to JSON file
    
    Args:
        config_data (dict): Configuration data to save
        filename (str): Filename (without extension)
        directory (str): Directory to save in
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        config_dir = Path(directory)
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Add timestamp and metadata
        enhanced_config = {
            'metadata': {
                'created': datetime.now().isoformat(),
                'version': '1.0.0',
                'type': 'pulse_jet_configuration'
            },
            'configuration': config_data
        }
        
        # Save to file
        filepath = config_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(enhanced_config, file, indent=2, ensure_ascii=False)
            
        return True
        
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return False


def load_configuration(filename: str, directory: str = "saved_configs") -> Dict[str, Any]:
    """
    Load configuration from JSON file
    
    Args:
        filename (str): Filename (with or without .json extension)
        directory (str): Directory to load from
        
    Returns:
        dict: Configuration data or empty dict if error
    """
    try:
        # Handle filename with or without extension
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = Path(directory) / filename
        
        if not filepath.exists():
            st.error(f"Configuration file {filename} not found.")
            return {}
            
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Extract configuration from enhanced format or return as-is
        if 'configuration' in data:
            return data['configuration']
        else:
            return data
            
    except json.JSONDecodeError as e:
        st.error(f"Error parsing JSON in {filename}: {e}")
        return {}
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return {}


def list_saved_configurations(directory: str = "saved_configs") -> List[str]:
    """
    List all saved configuration files
    
    Args:
        directory (str): Directory to search
        
    Returns:
        list: List of configuration filenames (without extension)
    """
    try:
        config_dir = Path(directory)
        if not config_dir.exists():
            return []
            
        config_files = []
        for file_path in config_dir.glob("*.json"):
            config_files.append(file_path.stem)
            
        return sorted(config_files)
        
    except Exception as e:
        st.warning(f"Error listing configurations: {e}")
        return []


# Data Handling Functions
def load_fuel_properties(file_path: str = "data/fuel_properties.json") -> Dict[str, Dict]:
    """
    Load fuel properties from JSON file with enhanced error handling
    
    Args:
        file_path (str): Path to fuel properties file
        
    Returns:
        dict: Fuel properties dictionary
    """
    try:
        fuel_file = Path(file_path)
        if fuel_file.exists():
            with open(fuel_file, 'r', encoding='utf-8') as file:
                fuel_data = json.load(file)
                
            # Validate fuel data structure
            if validate_fuel_properties(fuel_data):
                return fuel_data
            else:
                st.warning("Invalid fuel properties file structure. Using defaults.")
                return get_default_fuel_properties()
        else:
            st.info(f"Fuel properties file {file_path} not found. Using defaults.")
            return get_default_fuel_properties()
            
    except json.JSONDecodeError as e:
        st.error(f"Error parsing fuel properties JSON: {e}")
        return get_default_fuel_properties()
    except Exception as e:
        st.warning(f"Error loading fuel properties: {e}")
        return get_default_fuel_properties()


def get_default_fuel_properties() -> Dict[str, Dict]:
    """
    Get default fuel properties with comprehensive data
    
    Returns:
        dict: Default fuel properties
    """
    return {
        "Gasoline": {
            "heating_value": 44.0,      # MJ/kg
            "density": 0.75,            # kg/L at 15°C
            "stoich_ratio": 14.7,       # Air-fuel ratio
            "molecular_weight": 100,     # g/mol (average)
            "autoignition_temp": 280,    # °C
            "flash_point": -43,          # °C
            "boiling_point": 38,         # °C (initial)
            "octane_rating": 87,         # RON
            "vapor_pressure": 45         # kPa at 20°C
        },
        "Propane": {
            "heating_value": 46.4,
            "density": 0.51,
            "stoich_ratio": 15.7,
            "molecular_weight": 44,
            "autoignition_temp": 470,
            "flash_point": -104,
            "boiling_point": -42,
            "octane_rating": 112,
            "vapor_pressure": 853
        },
        "Hydrogen": {
            "heating_value": 120.0,
            "density": 0.0899,
            "stoich_ratio": 34.3,
            "molecular_weight": 2,
            "autoignition_temp": 500,
            "flash_point": -253,
            "boiling_point": -253,
            "octane_rating": 130,
            "vapor_pressure": 101325
        },
        "Kerosene": {
            "heating_value": 43.2,
            "density": 0.82,
            "stoich_ratio": 15.0,
            "molecular_weight": 170,
            "autoignition_temp": 210,
            "flash_point": 38,
            "boiling_point": 150,
            "octane_rating": 50,
            "vapor_pressure": 0.2
        }
    }


def validate_fuel_properties(fuel_data: Dict[str, Dict]) -> bool:
    """
    Validate fuel properties data structure
    
    Args:
        fuel_data (dict): Fuel properties to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ['heating_value', 'density', 'stoich_ratio', 'molecular_weight']
    
    try:
        for fuel_name, properties in fuel_data.items():
            if not isinstance(properties, dict):
                return False
                
            for field in required_fields:
                if field not in properties:
                    st.warning(f"Missing required field '{field}' for fuel '{fuel_name}'")
                    return False
                    
                if not isinstance(properties[field], (int, float)):
                    st.warning(f"Invalid type for field '{field}' in fuel '{fuel_name}'")
                    return False
                    
                if properties[field] <= 0:
                    st.warning(f"Non-positive value for '{field}' in fuel '{fuel_name}'")
                    return False
        
        return True
        
    except Exception as e:
        st.warning(f"Error validating fuel properties: {e}")
        return False


# Export and Import Functions
def export_results_to_csv(results_dict: Dict[str, Any], filename: str = None, 
                         directory: str = "exports") -> str:
    """
    Export results to CSV format with enhanced formatting
    
    Args:
        results_dict (dict): Results data to export
        filename (str, optional): Output filename
        directory (str): Export directory
        
    Returns:
        str: CSV data as string
    """
    try:
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pulse_jet_results_{timestamp}.csv"
        
        # Ensure directory exists
        export_dir = Path(directory)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for CSV
        csv_data = []
        for key, value in results_dict.items():
            # Format key for better readability
            formatted_key = format_parameter_name(key)
            
            # Format value with appropriate precision
            if isinstance(value, float):
                if abs(value) < 0.001:
                    formatted_value = f"{value:.6f}"
                elif abs(value) < 1:
                    formatted_value = f"{value:.4f}"
                elif abs(value) < 100:
                    formatted_value = f"{value:.2f}"
                else:
                    formatted_value = f"{value:.1f}"
            else:
                formatted_value = str(value)
            
            # Determine units
            units = get_parameter_units(key)
            if units:
                formatted_value += f" {units}"
            
            csv_data.append([formatted_key, formatted_value])
        
        # Add metadata
        csv_data.insert(0, ['Parameter', 'Value'])
        csv_data.insert(1, ['Generated', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        csv_data.insert(2, ['Software', 'Pulse Jet Modeler v1.0.0'])
        csv_data.insert(3, ['', ''])  # Empty row for separation
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_data[4:], columns=['Parameter', 'Value'])
        
        # Save to file
        filepath = export_dir / filename
        df.to_csv(filepath, index=False)
        
        # Return CSV string
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerows(csv_data)
        
        return output.getvalue()
        
    except Exception as e:
        st.error(f"Error exporting results: {e}")
        return ""


def export_results_to_excel(results_dict: Dict[str, Any], filename: str = None,
                           directory: str = "exports") -> bool:
    """
    Export results to Excel format with multiple sheets
    
    Args:
        results_dict (dict): Results data to export
        filename (str, optional): Output filename
        directory (str): Export directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if openpyxl is available
        try:
            import openpyxl
        except ImportError:
            st.warning("openpyxl not available. Install with: pip install openpyxl")
            return False
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"pulse_jet_results_{timestamp}.xlsx"
        
        # Ensure directory exists
        export_dir = Path(directory)
        export_dir.mkdir(parents=True, exist_ok=True)
        
        # Create Excel writer
        filepath = export_dir / filename
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Main results sheet
            results_df = pd.DataFrame([results_dict]).T
            results_df.columns = ['Value']
            results_df.index.name = 'Parameter'
            results_df.to_excel(writer, sheet_name='Performance Results')
            
            # Metadata sheet
            metadata = {
                'Generated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                'Software': ['Pulse Jet Modeler v1.0.0'],
                'Version': ['1.0.0'],
                'Description': ['Pulse jet engine performance analysis results']
            }
            metadata_df = pd.DataFrame(metadata)
            metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        return True
        
    except Exception as e:
        st.error(f"Error exporting to Excel: {e}")
        return False


def import_configuration_from_csv(filepath: str) -> Dict[str, Any]:
    """
    Import configuration from CSV file
    
    Args:
        filepath (str): Path to CSV file
        
    Returns:
        dict: Imported configuration data
    """
    try:
        df = pd.read_csv(filepath)
        
        # Convert back to dictionary format
        config = {}
        for _, row in df.iterrows():
            key = row.iloc[0]
            value = row.iloc[1]
            
            # Try to convert to appropriate type
            if isinstance(value, str):
                # Remove units and convert to float if possible
                clean_value = re.sub(r'[^\d.-]', '', value)
                try:
                    value = float(clean_value)
                except ValueError:
                    pass  # Keep as string
            
            config[key] = value
        
        return config
        
    except Exception as e:
        st.error(f"Error importing configuration: {e}")
        return {}


# Mathematical Utility Functions
def calculate_design_score(performance_results: Dict[str, float]) -> float:
    """
    Calculate overall design score based on performance metrics
    
    This function uses a weighted scoring system to evaluate overall design quality.
    The weights are based on typical pulse jet design priorities.
    
    Args:
        performance_results (dict): Performance metrics dictionary
        
    Returns:
        float: Design score (0-100)
    """
    try:
        # Scoring weights (must sum to 1.0)
        weights = {
            'thrust': 0.25,              # Primary performance metric
            'specific_impulse': 0.20,    # Fuel efficiency
            'thermal_efficiency': 0.20,  # Energy conversion efficiency
            'frequency': 0.15,           # Operating characteristics
            'thrust_to_weight_ratio': 0.10,  # Power density
            'power': 0.10                # Absolute power output
        }
        
        # Reference values for normalization (typical good values)
        references = {
            'thrust': 100.0,                    # N
            'specific_impulse': 150.0,          # s
            'thermal_efficiency': 25.0,         # %
            'frequency': 100.0,                 # Hz (optimal range center)
            'thrust_to_weight_ratio': 3.0,      # Dimensionless
            'power': 10.0                       # kW
        }
        
        # Calculate normalized scores
        normalized_scores = {}
        
        for metric, weight in weights.items():
            if metric in performance_results:
                value = performance_results[metric]
                reference = references[metric]
                
                if metric == 'frequency':
                    # Frequency has an optimal range (80-120 Hz)
                    if 80 <= value <= 120:
                        normalized_scores[metric] = 1.0
                    else:
                        # Penalty for being outside optimal range
                        distance = min(abs(value - 80), abs(value - 120))
                        normalized_scores[metric] = max(0, 1.0 - distance / 50)
                else:
                    # Linear normalization with saturation at reference value
                    normalized_scores[metric] = min(value / reference, 1.0)
            else:
                normalized_scores[metric] = 0.0
        
        # Calculate weighted score
        total_score = sum(weights[metric] * normalized_scores[metric] 
                         for metric in weights.keys())
        
        # Convert to percentage and apply quality curve
        score_percentage = total_score * 100
        
        # Apply a quality curve to make scores more discriminating
        # This makes it harder to achieve very high scores
        quality_adjusted_score = 100 * (1 - math.exp(-2.3 * total_score))
        
        return max(0, min(100, quality_adjusted_score))
        
    except Exception as e:
        st.warning(f"Error calculating design score: {e}")
        return 0.0


def interpolate_data(x_data: np.ndarray, y_data: np.ndarray, 
                    x_new: Union[float, np.ndarray], 
                    method: str = 'linear') -> Union[float, np.ndarray]:
    """
    Interpolate data with multiple methods
    
    Args:
        x_data (np.ndarray): X coordinates
        y_data (np.ndarray): Y coordinates
        x_new (float or np.ndarray): New X coordinates for interpolation
        method (str): Interpolation method ('linear', 'cubic', 'nearest')
        
    Returns:
        float or np.ndarray: Interpolated values
    """
    try:
        from scipy import interpolate
        
        if method == 'linear':
            f = interpolate.interp1d(x_data, y_data, kind='linear', 
                                   bounds_error=False, fill_value='extrapolate')
        elif method == 'cubic':
            f = interpolate.interp1d(x_data, y_data, kind='cubic',
                                   bounds_error=False, fill_value='extrapolate')
        elif method == 'nearest':
            f = interpolate.interp1d(x_data, y_data, kind='nearest',
                                   bounds_error=False, fill_value='extrapolate')
        else:
            raise ValueError(f"Unknown interpolation method: {method}")
        
        return f(x_new)
        
    except ImportError:
        st.warning("SciPy not available. Using simple linear interpolation.")
        return np.interp(x_new, x_data, y_data)
    except Exception as e:
        st.error(f"Error in interpolation: {e}")
        return x_new * 0  # Return zeros with same shape


def smooth_data(data: np.ndarray, window_size: int = 5, method: str = 'moving_average') -> np.ndarray:
    """
    Smooth data using various methods
    
    Args:
        data (np.ndarray): Data to smooth
        window_size (int): Size of smoothing window
        method (str): Smoothing method ('moving_average', 'gaussian', 'savgol')
        
    Returns:
        np.ndarray: Smoothed data
    """
    try:
        if len(data) < window_size:
            return data
        
        if method == 'moving_average':
            # Simple moving average
            smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        elif method == 'gaussian':
            # Gaussian smoothing
            from scipy import ndimage
            sigma = window_size / 3.0
            smoothed = ndimage.gaussian_filter1d(data, sigma)
        elif method == 'savgol':
            # Savitzky-Golay filter
            from scipy import signal
            smoothed = signal.savgol_filter(data, window_size, 3)
        else:
            st.warning(f"Unknown smoothing method: {method}. Using moving average.")
            smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        return smoothed
        
    except ImportError:
        st.warning("SciPy not available for advanced smoothing. Using simple moving average.")
        return np.convolve(data, np.ones(window_size)/window_size, mode='same')
    except Exception as e:
        st.error(f"Error in data smoothing: {e}")
        return data


# Unit Conversion Functions
def convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between different units
    
    Args:
        value (float): Value to convert
        from_unit (str): Source unit
        to_unit (str): Target unit
        
    Returns:
        float: Converted value
    """
    # Length conversions
    length_to_meters = {
        'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0,
        'in': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mi': 1609.34
    }
    
    # Mass conversions
    mass_to_kg = {
        'g': 0.001, 'kg': 1.0, 'lb': 0.453592, 'oz': 0.0283495, 't': 1000.0
    }
    
    # Pressure conversions
    pressure_to_pa = {
        'Pa': 1.0, 'kPa': 1000.0, 'MPa': 1e6, 'bar': 1e5,
        'psi': 6894.76, 'atm': 101325.0, 'mmHg': 133.322, 'Torr': 133.322
    }
    
    # Temperature conversions (special case)
    if from_unit in ['C', 'F', 'K'] and to_unit in ['C', 'F', 'K']:
        return convert_temperature(value, from_unit, to_unit)
    
    # General conversion using dictionaries
    conversion_tables = {
        'length': length_to_meters,
        'mass': mass_to_kg,
        'pressure': pressure_to_pa
    }
    
    for table_name, table in conversion_tables.items():
        if from_unit in table and to_unit in table:
            # Convert to base unit then to target unit
            base_value = value * table[from_unit]
            return base_value / table[to_unit]
    
    # If no conversion found, return original value
    st.warning(f"No conversion available from {from_unit} to {to_unit}")
    return value


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """
    Convert between temperature units
    
    Args:
        value (float): Temperature value
        from_unit (str): Source unit ('C', 'F', 'K')
        to_unit (str): Target unit ('C', 'F', 'K')
        
    Returns:
        float: Converted temperature
    """
    # Convert to Celsius first
    if from_unit == 'F':
        celsius = (value - 32) * 5/9
    elif from_unit == 'K':
        celsius = value - 273.15
    else:  # from_unit == 'C'
        celsius = value
    
    # Convert from Celsius to target
    if to_unit == 'F':
        return celsius * 9/5 + 32
    elif to_unit == 'K':
        return celsius + 273.15
    else:  # to_unit == 'C'
        return celsius


# Formatting Functions
def format_parameter_value(value: float, unit: str = "", decimals: int = 2,
                          use_si_prefix: bool = True) -> str:
    """
    Format parameter value with appropriate units and precision
    
    Args:
        value (float): Value to format
        unit (str): Unit string
        decimals (int): Number of decimal places
        use_si_prefix (bool): Whether to use SI prefixes (k, M, etc.)
        
    Returns:
        str: Formatted value string
    """
    try:
        if math.isnan(value) or math.isinf(value):
            return f"--{' ' + unit if unit else ''}"
        
        if use_si_prefix and abs(value) >= 1000:
            if abs(value) >= 1000000000:
                formatted_value = f"{value/1000000000:.{decimals}f}G"
            elif abs(value) >= 1000000:
                formatted_value = f"{value/1000000:.{decimals}f}M"
            elif abs(value) >= 1000:
                formatted_value = f"{value/1000:.{decimals}f}k"
            else:
                formatted_value = f"{value:.{decimals}f}"
        elif use_si_prefix and abs(value) < 1 and value != 0:
            if abs(value) < 0.001:
                formatted_value = f"{value*1000000:.{decimals}f}μ"
            elif abs(value) < 1:
                formatted_value = f"{value*1000:.{decimals}f}m"
            else:
                formatted_value = f"{value:.{decimals}f}"
        else:
            formatted_value = f"{value:.{decimals}f}"
        
        return f"{formatted_value}{' ' + unit if unit else ''}"
        
    except Exception as e:
        st.warning(f"Error formatting value {value}: {e}")
        return f"{value}{' ' + unit if unit else ''}"


def format_parameter_name(param_name: str) -> str:
    """
    Format parameter name for display
    
    Args:
        param_name (str): Parameter name to format
        
    Returns:
        str: Formatted parameter name
    """
    # Dictionary of parameter name mappings
    name_mappings = {
        'thrust': 'Thrust',
        'specific_impulse': 'Specific Impulse',
        'thermal_efficiency': 'Thermal Efficiency',
        'frequency': 'Operating Frequency',
        'air_mass_flow': 'Air Mass Flow',
        'fuel_mass_flow': 'Fuel Mass Flow',
        'exhaust_velocity': 'Exhaust Velocity',
        'power': 'Power Output',
        'combustion_volume': 'Combustion Volume',
        'intake_area': 'Intake Area',
        'exhaust_area': 'Exhaust Area',
        'combustion_chamber_length': 'Chamber Length',
        'combustion_chamber_diameter': 'Chamber Diameter',
        'intake_diameter': 'Intake Diameter',
        'exhaust_diameter': 'Exhaust Diameter',
        'exhaust_length': 'Exhaust Length',
        'valve_area': 'Valve Area',
        'num_valves': 'Number of Valves',
        'air_fuel_ratio': 'Air-Fuel Ratio',
        'ambient_pressure': 'Ambient Pressure',
        'ambient_temp': 'Ambient Temperature',
        'fuel_consumption_rate': 'Fuel Consumption Rate',
        'specific_fuel_consumption': 'Specific Fuel Consumption',
        'thrust_to_weight_ratio': 'Thrust-to-Weight Ratio',
        'power_to_weight_ratio': 'Power-to-Weight Ratio'
    }
    
    # Return mapped name or format the original
    if param_name in name_mappings:
        return name_mappings[param_name]
    else:
        # Convert snake_case to Title Case
        formatted = param_name.replace('_', ' ').title()
        return formatted


def get_parameter_units(param_name: str) -> str:
    """
    Get appropriate units for a parameter
    
    Args:
        param_name (str): Parameter name
        
    Returns:
        str: Units string
    """
    unit_mappings = {
        'thrust': 'N',
        'specific_impulse': 's',
        'thermal_efficiency': '%',
        'frequency': 'Hz',
        'air_mass_flow': 'kg/s',
        'fuel_mass_flow': 'kg/s',
        'exhaust_velocity': 'm/s',
        'power': 'kW',
        'combustion_volume': 'L',
        'intake_area': 'cm²',
        'exhaust_area': 'cm²',
        'combustion_chamber_length': 'cm',
        'combustion_chamber_diameter': 'cm',
        'intake_diameter': 'cm',
        'exhaust_diameter': 'cm',
        'exhaust_length': 'cm',
        'valve_area': 'cm²',
        'num_valves': '',
        'air_fuel_ratio': '',
        'ambient_pressure': 'kPa',
        'ambient_temp': '°C',
        'fuel_consumption_rate': 'kg/h',
        'specific_fuel_consumption': 'kg/kW·h',
        'thrust_to_weight_ratio': '',
        'power_to_weight_ratio': 'kW/kg'
    }
    
    return unit_mappings.get(param_name, '')


# Report Generation Functions
def generate_design_report(geometry_params: Dict, performance_results: Dict, 
                         suggestions: Dict[str, str], include_theory: bool = False) -> str:
    """
    Generate a comprehensive design report in markdown format
    
    Args:
        geometry_params (dict): Engine geometry parameters
        performance_results (dict): Performance analysis results
        suggestions (dict): Design optimization suggestions
        include_theory (bool): Whether to include theoretical background
        
    Returns:
        str: Markdown formatted report
    """
    try:
        # Calculate design score
        score = calculate_design_score(performance_results)
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Start building the report
        report = f"""# Pulse Jet Engine Design Report

**Generated:** {timestamp}  
**Software:** Pulse Jet Modeler v1.0.0  
**Report Type:** Comprehensive Design Analysis

---

## Executive Summary

**Overall Design Score:** {score:.1f}/100

### Key Performance Highlights
- **Thrust Output:** {format_parameter_value(performance_results.get('thrust', 0), 'N', 1)}
- **Specific Impulse:** {format_parameter_value(performance_results.get('specific_impulse', 0), 's', 0)}
- **Thermal Efficiency:** {format_parameter_value(performance_results.get('thermal_efficiency', 0), '%', 1)}
- **Operating Frequency:** {format_parameter_value(performance_results.get('frequency', 0), 'Hz', 0)}

### Design Classification
"""
        
        # Add design classification based on score
        if score >= 80:
            report += "🏆 **Excellent Design** - Outstanding performance across all metrics\n"
        elif score >= 65:
            report += "✅ **Good Design** - Strong performance with minor optimization opportunities\n"
        elif score >= 50:
            report += "⚠️ **Acceptable Design** - Meets basic requirements but has improvement potential\n"
        else:
            report += "❌ **Needs Improvement** - Significant optimization required\n"
        
        report += """
---

## Engine Configuration

### Geometry Specifications
"""
        
        # Add geometry details
        if 'combustion_chamber_length' in geometry_params:
            length = geometry_params['combustion_chamber_length']
            diameter = geometry_params['combustion_chamber_diameter']
            ld_ratio = length / diameter if diameter > 0 else 0
            
            report += f"""
| Parameter | Value | Notes |
|-----------|-------|-------|
| **Combustion Chamber** | {length:.0f} × {diameter:.0f} cm | L/D ratio: {ld_ratio:.1f} |
| **Intake Diameter** | {geometry_params.get('intake_diameter', 0):.0f} cm | |
| **Exhaust Diameter** | {geometry_params.get('exhaust_diameter', 0):.0f} cm | |
| **Exhaust Length** | {geometry_params.get('exhaust_length', 0):.0f} cm | |
| **Combustion Volume** | {performance_results.get('combustion_volume', 0):.2f} L | |
"""
        
        report += """
### Valve System
"""
        
        # Add valve information if available
        valve_info = geometry_params.get('valve_type', 'Not specified')
        num_valves = geometry_params.get('num_valves', 'Not specified')
        valve_area = geometry_params.get('valve_area', 'Not specified')
        
        report += f"""
- **Type:** {valve_info}
- **Quantity:** {num_valves}
- **Total Area:** {valve_area} cm²
"""
        
        report += """
---

## Performance Analysis

### Primary Metrics
"""
        
        # Performance metrics table
        metrics = [
            ('Thrust', performance_results.get('thrust', 0), 'N', 'Primary propulsive force'),
            ('Specific Impulse', performance_results.get('specific_impulse', 0), 's', 'Fuel efficiency measure'),
            ('Power Output', performance_results.get('power', 0), 'kW', 'Mechanical power equivalent'),
            ('Thermal Efficiency', performance_results.get('thermal_efficiency', 0), '%', 'Energy conversion efficiency')
        ]
        
        report += "\n| Metric | Value | Description |\n|--------|-------|-------------|\n"
        for name, value, unit, description in metrics:
            formatted_value = format_parameter_value(value, unit, 2)
            report += f"| **{name}** | {formatted_value} | {description} |\n"
        
        report += """
### Operating Characteristics
"""
        
        # Operating characteristics
        operating_metrics = [
            ('Operating Frequency', performance_results.get('frequency', 0), 'Hz'),
            ('Air Mass Flow', performance_results.get('air_mass_flow', 0), 'kg/s'),
            ('Fuel Mass Flow', performance_results.get('fuel_mass_flow', 0), 'kg/s'),
            ('Exhaust Velocity', performance_results.get('exhaust_velocity', 0), 'm/s'),
            ('Fuel Consumption', performance_results.get('fuel_consumption_rate', 0), 'kg/h')
        ]
        
        report += "\n| Parameter | Value |\n|-----------|-------|\n"
        for name, value, unit in operating_metrics:
            formatted_value = format_parameter_value(value, unit, 3)
            report += f"| {name} | {formatted_value} |\n"
        
        report += """
---

## Design Analysis & Recommendations
"""
        
        # Add suggestions
        if suggestions:
            report += "\n### Optimization Opportunities\n\n"
            for category, suggestion in suggestions.items():
                category_formatted = format_parameter_name(category)
                report += f"**{category_formatted}:** {suggestion}\n\n"
        else:
            report += "\n✅ **No significant issues identified.** Current design parameters are well-balanced.\n\n"
        
        report += """
### Design Trade-offs

This analysis reveals several key trade-offs in your design:

1. **Performance vs. Efficiency:** Higher thrust typically comes at the cost of fuel efficiency
2. **Frequency vs. Durability:** Higher operating frequencies increase power density but may reduce component life
3. **Size vs. Weight:** Larger engines produce more thrust but increase overall system weight
4. **Complexity vs. Reliability:** More sophisticated valve systems may improve performance but increase failure modes

### Recommended Next Steps

1. **Validation Testing:** Build and test a prototype to validate these theoretical predictions
2. **Materials Selection:** Choose appropriate materials for the operating temperature and frequency
3. **Manufacturing Considerations:** Ensure design can be manufactured within required tolerances
4. **Safety Analysis:** Conduct thorough safety assessment for intended operating conditions
"""
        
        # Add theoretical background if requested
        if include_theory:
            report += """
---

## Theoretical Background

### Model Foundations

This analysis is based on the following theoretical models:

#### Frequency Calculation
The operating frequency is calculated using Helmholtz resonator theory:

```
f = (c/2π) × √(A_neck/(V_chamber × L_eff))
```

Where:
- `c` = speed of sound at operating temperature
- `A_neck` = effective exhaust area
- `V_chamber` = combustion chamber volume
- `L_eff` = effective exhaust length with end corrections

#### Thrust Calculation
Thrust is calculated using momentum theory:

```
F = ṁ × V_exhaust + (P_exhaust - P_ambient) × A_exhaust
```

Where:
- `ṁ` = total mass flow rate
- `V_exhaust` = exhaust velocity
- `P_exhaust` = exhaust pressure
- `A_exhaust` = exhaust area

#### Efficiency Calculation
Thermal efficiency is based on energy conversion:

```
η_thermal = P_propulsive / P_fuel × 100%
```

Where propulsive power is derived from thrust and exhaust velocity relationships.
"""
        
        report += f"""
---

## Disclaimers and Limitations

⚠️ **Important Notice:** This analysis is based on simplified theoretical models for preliminary design purposes. Actual performance will depend on many factors not included in this model:

- Manufacturing tolerances and surface finish
- Real combustion dynamics and heat transfer
- Valve dynamics and timing effects
- Acoustic coupling and resonance effects
- Operating environment variations

### Model Accuracy
- **Thrust predictions:** ±30-50% typical accuracy
- **Frequency calculations:** ±20-30% typical accuracy  
- **Efficiency estimates:** ±40-60% typical accuracy

### Recommended Validation
Always validate designs through:
1. Computational fluid dynamics (CFD) analysis
2. Bench testing and measurement
3. Professional engineering review
4. Safety assessment and certification

---

**Report Generated by Pulse Jet Modeler v1.0.0**  
*For technical support and updates, visit: https://github.com/your-username/pulse-jet-modeler*
"""
        
        return report
        
    except Exception as e:
        st.error(f"Error generating design report: {e}")
        return f"# Error Generating Report\n\nAn error occurred: {str(e)}"


def create_comparison_table(designs: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Create comparison table for multiple designs
    
    Args:
        designs (list): List of design dictionaries
        
    Returns:
        pd.DataFrame: Comparison table
    """
    try:
        if not designs:
            return pd.DataFrame()
        
        comparison_data = []
        
        for i, design in enumerate(designs):
            # Extract performance data
            if 'results' in design:
                results = design['results']
            else:
                results = design
            
            # Calculate design score
            score = calculate_design_score(results)
            
            # Create row data
            row_data = {
                'Design': f"Design {i+1}",
                'Thrust (N)': results.get('thrust', 0),
                'Frequency (Hz)': results.get('frequency', 0),
                'Specific Impulse (s)': results.get('specific_impulse', 0),
                'Efficiency (%)': results.get('thermal_efficiency', 0),
                'Power (kW)': results.get('power', 0),
                'Score': score
            }
            
            # Add geometry data if available
            if 'geometry' in design:
                geom = design['geometry']
                row_data['L/D Ratio'] = (geom.get('combustion_chamber_length', 0) / 
                                       geom.get('combustion_chamber_diameter', 1))
                row_data['Chamber Vol (L)'] = results.get('combustion_volume', 0)
            
            comparison_data.append(row_data)
        
        # Create DataFrame
        df = pd.DataFrame(comparison_data)
        
        # Format numeric columns
        numeric_columns = ['Thrust (N)', 'Frequency (Hz)', 'Specific Impulse (s)', 
                          'Efficiency (%)', 'Power (kW)', 'Score']
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].round(1)
        
        return df
        
    except Exception as e:
        st.error(f"Error creating comparison table: {e}")
        return pd.DataFrame()


def create_performance_summary(results: Dict[str, float], geometry: Dict[str, float] = None) -> str:
    """
    Create a concise performance summary
    
    Args:
        results (dict): Performance results
        geometry (dict, optional): Geometry parameters
        
    Returns:
        str: Formatted performance summary
    """
    try:
        summary = "🚀 **Pulse Jet Performance Summary**\n\n"
        
        # Key metrics
        thrust = results.get('thrust', 0)
        frequency = results.get('frequency', 0)
        efficiency = results.get('thermal_efficiency', 0)
        isp = results.get('specific_impulse', 0)
        
        summary += f"**Thrust:** {format_parameter_value(thrust, 'N', 1)} "
        summary += f"({format_parameter_value(thrust/9.81, 'kgf', 1)})\n"
        summary += f"**Frequency:** {format_parameter_value(frequency, 'Hz', 0)}\n"
        summary += f"**Efficiency:** {format_parameter_value(efficiency, '%', 1)}\n"
        summary += f"**Specific Impulse:** {format_parameter_value(isp, 's', 0)}\n\n"
        
        # Design quality assessment
        score = calculate_design_score(results)
        if score >= 75:
            summary += "✅ **Excellent design** with strong performance\n"
        elif score >= 60:
            summary += "👍 **Good design** with solid performance\n"
        elif score >= 45:
            summary += "⚠️ **Adequate design** with improvement potential\n"
        else:
            summary += "❌ **Needs optimization** for better performance\n"
        
        # Add geometry info if available
        if geometry:
            length = geometry.get('combustion_chamber_length', 0)
            diameter = geometry.get('combustion_chamber_diameter', 0)
            if diameter > 0:
                ld_ratio = length / diameter
                summary += f"\n**Geometry:** {length:.0f}×{diameter:.0f} cm (L/D: {ld_ratio:.1f})\n"
        
        return summary
        
    except Exception as e:
        st.warning(f"Error creating performance summary: {e}")
        return "Error creating summary"


# File and Directory Utilities
def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure a directory exists, creating it if necessary
    
    Args:
        directory_path (str): Path to directory
        
    Returns:
        bool: True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        st.error(f"Error creating directory {directory_path}: {e}")
        return False


def clean_old_files(directory: str, days_old: int = 30, pattern: str = "*") -> int:
    """
    Clean old files from a directory
    
    Args:
        directory (str): Directory to clean
        days_old (int): Delete files older than this many days
        pattern (str): File pattern to match
        
    Returns:
        int: Number of files deleted
    """
    try:
        directory_path = Path(directory)
        if not directory_path.exists():
            return 0
        
        import time
        current_time = time.time()
        cutoff_time = current_time - (days_old * 24 * 60 * 60)
        
        deleted_count = 0
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                file_time = file_path.stat().st_mtime
                if file_time < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
        
        return deleted_count
        
    except Exception as e:
        st.warning(f"Error cleaning old files: {e}")
        return 0


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        filepath (str): Path to file
        
    Returns:
        float: File size in MB
    """
    try:
        size_bytes = Path(filepath).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


# Package Metadata and Information
def get_package_info() -> Dict[str, str]:
    """
    Get package information
    
    Returns:
        dict: Package metadata
    """
    return {
        'name': 'Pulse Jet Modeler',
        'version': '1.0.0',
        'author': 'Pulse Jet Modeler Contributors',
        'license': 'MIT',
        'description': 'A comprehensive tool for pulse jet engine design and performance modeling',
        'homepage': 'https://github.com/your-username/pulse-jet-modeler',
        'documentation': 'https://pulse-jet-modeler.readthedocs.io/',
        'support': 'https://github.com/your-username/pulse-jet-modeler/issues'
    }


def print_package_info():
    """Print package information to console"""
    info = get_package_info()
    print(f"\n{info['name']} v{info['version']}")
    print(f"Author: {info['author']}")
    print(f"License: {info['license']}")
    print(f"Homepage: {info['homepage']}")
    print(f"Description: {info['description']}\n")


# Export all public functions
__all__ = [
    # Configuration management
    'load_config',
    'get_default_config', 
    'save_configuration',
    'load_configuration',
    'list_saved_configurations',
    
    # Data handling
    'load_fuel_properties',
    'get_default_fuel_properties',
    'validate_fuel_properties',
    
    # Export/Import
    'export_results_to_csv',
    'export_results_to_excel',
    'import_configuration_from_csv',
    
    # Mathematical utilities
    'calculate_design_score',
    'interpolate_data',
    'smooth_data',
    
    # Unit conversions
    'convert_units',
    'convert_temperature',
    
    # Formatting
    'format_parameter_value',
    'format_parameter_name',
    'get_parameter_units',
    
    # Report generation
    'generate_design_report',
    'create_comparison_table',
    'create_performance_summary',
    
    # File utilities
    'ensure_directory_exists',
    'clean_old_files',
    'get_file_size_mb',
    
    # Package info
    'get_package_info',
    'print_package_info'
]
