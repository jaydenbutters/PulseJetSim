"""
Pulse Jet Engine Performance Models

This module contains the core mathematical models for pulse jet engine
performance analysis including thermodynamic calculations, frequency
analysis, and performance predictions.

The models are based on simplified but physically sound principles:
- Helmholtz resonator theory for frequency calculation
- Thermodynamic cycle analysis for performance prediction
- Empirical correlations for valve and combustion modeling
- Conservation of mass, momentum, and energy

Classes:
    EngineGeometry: Engine dimensional parameters
    ValveSystem: Valve configuration parameters
    OperatingConditions: Operating environment parameters
    PerformanceResults: Calculated performance metrics
    PulseJetModel: Main analysis engine
    OptimizationAnalyzer: Design optimization tools

Example:
    Basic usage:
    
    >>> from pulse_jet_models import *
    >>> 
    >>> # Create model
    >>> model = PulseJetModel()
    >>> 
    >>> # Define geometry
    >>> geometry = EngineGeometry(
    ...     combustion_chamber_length=50,
    ...     combustion_chamber_diameter=15,
    ...     intake_diameter=8,
    ...     exhaust_diameter=10,
    ...     exhaust_length=80
    ... )
    >>> 
    >>> # Define valves
    >>> valves = ValveSystem(
    ...     valve_type="Reed Valves",
    ...     num_valves=4,
    ...     valve_area=20
    ... )
    >>> 
    >>> # Define conditions
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

import numpy as np
import math
import warnings
from typing import Dict, Tuple, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
import json

# Try to import utils for fuel properties, with fallback
try:
    from .utils import load_fuel_properties
except ImportError:
    # Fallback function if utils not available
    def load_fuel_properties():
        """Fallback fuel properties"""
        return {
            "Gasoline": {"heating_value": 44.0, "density": 0.75, "stoich_ratio": 14.7},
            "Propane": {"heating_value": 46.4, "density": 0.51, "stoich_ratio": 15.7},
            "Hydrogen": {"heating_value": 120.0, "density": 0.0899, "stoich_ratio": 34.3},
            "Kerosene": {"heating_value": 43.2, "density": 0.82, "stoich_ratio": 15.0}
        }


@dataclass
class EngineGeometry:
    """
    Engine geometry parameters
    
    Attributes:
        combustion_chamber_length (float): Length of combustion chamber (cm)
        combustion_chamber_diameter (float): Diameter of combustion chamber (cm)
        intake_diameter (float): Diameter of intake (cm)
        exhaust_diameter (float): Diameter of exhaust (cm)
        exhaust_length (float): Length of exhaust pipe (cm)
    """
    combustion_chamber_length: float  # cm
    combustion_chamber_diameter: float  # cm
    intake_diameter: float  # cm
    exhaust_diameter: float  # cm
    exhaust_length: float  # cm
    
    def __post_init__(self):
        """Validate geometry parameters after initialization"""
        if self.combustion_chamber_length <= 0:
            raise ValueError("Combustion chamber length must be positive")
        if self.combustion_chamber_diameter <= 0:
            raise ValueError("Combustion chamber diameter must be positive")
        if self.intake_diameter <= 0:
            raise ValueError("Intake diameter must be positive")
        if self.exhaust_diameter <= 0:
            raise ValueError("Exhaust diameter must be positive")
        if self.exhaust_length <= 0:
            raise ValueError("Exhaust length must be positive")
    
    @property
    def combustion_volume(self) -> float:
        """Calculate combustion chamber volume in liters"""
        return math.pi * (self.combustion_chamber_diameter/2)**2 * self.combustion_chamber_length / 1000
    
    @property
    def intake_area(self) -> float:
        """Calculate intake cross-sectional area in cm²"""
        return math.pi * (self.intake_diameter/2)**2
    
    @property
    def exhaust_area(self) -> float:
        """Calculate exhaust cross-sectional area in cm²"""
        return math.pi * (self.exhaust_diameter/2)**2
    
    @property
    def ld_ratio(self) -> float:
        """Calculate length-to-diameter ratio"""
        return self.combustion_chamber_length / self.combustion_chamber_diameter
    
    @property
    def area_ratio(self) -> float:
        """Calculate exhaust-to-intake area ratio"""
        return self.exhaust_area / self.intake_area


@dataclass
class ValveSystem:
    """
    Valve system parameters
    
    Attributes:
        valve_type (str): Type of valves ("Reed Valves", "Flapper Valves", "Rotary Valves")
        num_valves (int): Number of valves
        valve_area (float): Total valve area (cm²)
    """
    valve_type: str
    num_valves: int
    valve_area: float  # cm²
    
    def __post_init__(self):
        """Validate valve parameters after initialization"""
        valid_types = ["Reed Valves", "Flapper Valves", "Rotary Valves"]
        if self.valve_type not in valid_types:
            raise ValueError(f"Valve type must be one of: {valid_types}")
        if self.num_valves <= 0:
            raise ValueError("Number of valves must be positive")
        if self.valve_area <= 0:
            raise ValueError("Valve area must be positive")
    
    @property
    def valve_area_per_valve(self) -> float:
        """Calculate area per individual valve"""
        return self.valve_area / self.num_valves


@dataclass
class OperatingConditions:
    """
    Operating condition parameters
    
    Attributes:
        fuel_type (str): Type of fuel ("Gasoline", "Propane", "Hydrogen", "Kerosene")
        air_fuel_ratio (float): Air-to-fuel mass ratio
        ambient_pressure (float): Ambient pressure (kPa)
        ambient_temp (float): Ambient temperature (°C)
    """
    fuel_type: str
    air_fuel_ratio: float
    ambient_pressure: float  # kPa
    ambient_temp: float  # °C
    
    def __post_init__(self):
        """Validate operating conditions after initialization"""
        valid_fuels = ["Gasoline", "Propane", "Hydrogen", "Kerosene"]
        if self.fuel_type not in valid_fuels:
            raise ValueError(f"Fuel type must be one of: {valid_fuels}")
        if self.air_fuel_ratio <= 0:
            raise ValueError("Air-fuel ratio must be positive")
        if self.ambient_pressure <= 0:
            raise ValueError("Ambient pressure must be positive")
    
    @property
    def ambient_temp_kelvin(self) -> float:
        """Get ambient temperature in Kelvin"""
        return self.ambient_temp + 273.15


@dataclass
class PerformanceResults:
    """
    Engine performance results
    
    All calculated performance metrics from the analysis
    """
    # Geometry-derived parameters
    combustion_volume: float  # L
    intake_area: float  # cm²
    exhaust_area: float  # cm²
    
    # Operating parameters
    frequency: float  # Hz
    air_mass_flow: float  # kg/s
    fuel_mass_flow: float  # kg/s
    exhaust_velocity: float  # m/s
    
    # Performance metrics
    thrust: float  # N
    specific_impulse: float  # s
    power: float  # kW
    thermal_efficiency: float  # %
    specific_fuel_consumption: float  # kg/kW·h
    
    # Additional derived metrics
    thrust_to_weight_ratio: float = field(default=0.0)  # Assuming engine weight
    power_to_weight_ratio: float = field(default=0.0)  # kW/kg
    fuel_consumption_rate: float = field(default=0.0)  # kg/h
    
    def __post_init__(self):
        """Calculate additional derived metrics"""
        # Assume typical engine weight of 5kg per kW for pulse jets
        estimated_engine_weight = max(self.power * 5, 10)  # kg, minimum 10kg
        
        self.thrust_to_weight_ratio = self.thrust / (estimated_engine_weight * 9.81)
        self.power_to_weight_ratio = self.power / estimated_engine_weight
        self.fuel_consumption_rate = self.fuel_mass_flow * 3600  # kg/h


class PulseJetModel:
    """
    Main pulse jet performance model
    
    This class implements the core physics-based models for pulse jet
    engine performance analysis. It uses simplified but physically
    sound principles to estimate engine performance.
    
    The model includes:
    - Helmholtz resonator frequency calculation
    - Mass flow analysis based on valve dynamics
    - Thermodynamic cycle analysis
    - Thrust and efficiency calculations
    
    Attributes:
        fuel_properties (dict): Fuel properties database
        constants (dict): Physical and model constants
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the pulse jet model
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        self.fuel_properties = load_fuel_properties()
        
        # Load constants from config or use defaults
        if config_file and Path(config_file).exists():
            self._load_config(config_file)
        else:
            self._set_default_constants()
    
    def _load_config(self, config_file: str):
        """Load constants from configuration file"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.constants = config.get('model', {}).get('constants', self._get_default_constants())
        except Exception:
            warnings.warn(f"Could not load config file {config_file}, using defaults")
            self._set_default_constants()
    
    def _set_default_constants(self):
        """Set default model constants"""
        self.constants = self._get_default_constants()
    
    def _get_default_constants(self) -> Dict[str, float]:
        """Get default model constants"""
        return {
            'R': 287,  # Specific gas constant for air (J/kg·K)
            'gamma': 1.4,  # Heat capacity ratio for air
            'g': 9.81,  # Standard gravity (m/s²)
            'frequency_constant': 17000,  # Helmholtz resonator constant
            'combustion_efficiency': 0.85,  # Combustion efficiency (0-1)
            'valve_discharge_coeff': 0.8,  # Valve discharge coefficient (0-1)
            'exhaust_efficiency': 0.95,  # Exhaust nozzle efficiency (0-1)
            'end_correction_factor': 0.6,  # End correction for Helmholtz calculation
            'mixing_efficiency': 0.9,  # Air-fuel mixing efficiency (0-1)
            'heat_transfer_factor': 0.85  # Heat transfer efficiency (0-1)
        }
    
    def calculate_geometry_parameters(self, geometry: EngineGeometry) -> Dict[str, float]:
        """
        Calculate derived geometry parameters
        
        Args:
            geometry (EngineGeometry): Engine geometry object
            
        Returns:
            dict: Dictionary containing calculated geometry parameters
        """
        return {
            'combustion_volume': geometry.combustion_volume,
            'intake_area': geometry.intake_area,
            'exhaust_area': geometry.exhaust_area,
            'area_ratio': geometry.area_ratio,
            'ld_ratio': geometry.ld_ratio,
            'surface_area': self._calculate_surface_area(geometry),
            'volume_to_surface_ratio': geometry.combustion_volume / self._calculate_surface_area(geometry)
        }
    
    def _calculate_surface_area(self, geometry: EngineGeometry) -> float:
        """Calculate combustion chamber surface area for heat transfer"""
        # Cylindrical chamber surface area in m²
        radius = geometry.combustion_chamber_diameter / 200  # Convert cm to m
        length = geometry.combustion_chamber_length / 100   # Convert cm to m
        
        # Surface area = 2πr² + 2πrh (cylinder with both ends)
        surface_area = 2 * math.pi * radius**2 + 2 * math.pi * radius * length
        return surface_area
    
    def calculate_operating_frequency(self, geometry: EngineGeometry, 
                                    conditions: OperatingConditions) -> float:
        """
        Calculate operating frequency using enhanced Helmholtz resonator model
        
        This model includes:
        - Temperature effects on sound speed
        - End corrections for finite pipe diameter
        - Pressure effects on gas properties
        
        Args:
            geometry (EngineGeometry): Engine geometry
            conditions (OperatingConditions): Operating conditions
            
        Returns:
            float: Operating frequency in Hz
        """
        # Calculate sound speed at operating temperature
        temp_kelvin = conditions.ambient_temp_kelvin
        sound_speed = math.sqrt(self.constants['gamma'] * self.constants['R'] * temp_kelvin)
        
        # Calculate effective lengths with end corrections
        end_correction = self.constants['end_correction_factor']
        effective_exhaust_length = (geometry.exhaust_length + 
                                   end_correction * geometry.exhaust_diameter)  # cm
        effective_intake_length = end_correction * geometry.intake_diameter  # cm
        
        # Total effective neck length
        total_neck_length = effective_exhaust_length + effective_intake_length  # cm
        
        # Convert to meters for calculation
        volume_m3 = geometry.combustion_volume / 1000  # L to m³
        neck_area_m2 = geometry.exhaust_area / 10000   # cm² to m²
        neck_length_m = total_neck_length / 100        # cm to m
        
        # Helmholtz frequency calculation
        if volume_m3 > 0 and neck_length_m > 0:
            frequency = (sound_speed / (2 * math.pi)) * math.sqrt(neck_area_m2 / (volume_m3 * neck_length_m))
        else:
            frequency = 0
        
        return frequency
    
    def calculate_mass_flows(self, geometry: EngineGeometry, valves: ValveSystem,
                           conditions: OperatingConditions, frequency: float) -> Tuple[float, float]:
        """
        Calculate air and fuel mass flow rates
        
        This model estimates mass flows based on:
        - Valve area and discharge characteristics
        - Operating frequency and duty cycle
        - Ambient conditions and air density
        - Compressible flow effects
        
        Args:
            geometry (EngineGeometry): Engine geometry
            valves (ValveSystem): Valve system configuration
            conditions (OperatingConditions): Operating conditions
            frequency (float): Operating frequency in Hz
            
        Returns:
            tuple: (air_mass_flow, fuel_mass_flow) in kg/s
        """
        # Calculate air density at ambient conditions
        temp_kelvin = conditions.ambient_temp_kelvin
        pressure_pa = conditions.ambient_pressure * 1000  # kPa to Pa
        air_density = pressure_pa / (self.constants['R'] * temp_kelvin)  # kg/m³
        
        # Effective valve area accounting for discharge coefficient and number of valves
        effective_valve_area = (valves.valve_area * self.constants['valve_discharge_coeff'] / 10000)  # m²
        
        # Characteristic velocity for compressible flow
        # This is a simplified model - real valve dynamics are much more complex
        characteristic_velocity = math.sqrt(2 * pressure_pa / air_density)  # m/s
        
        # Duty cycle estimation (fraction of time valves are open)
        # Higher frequencies typically have lower duty cycles
        if frequency > 0:
            duty_cycle = min(0.4, 50 / frequency)  # Empirical relationship
        else:
            duty_cycle = 0.3
        
        # Volumetric flow rate
        volumetric_flow = effective_valve_area * characteristic_velocity * duty_cycle  # m³/s
        
        # Air mass flow rate
        air_mass_flow = air_density * volumetric_flow * self.constants['mixing_efficiency']  # kg/s
        
        # Fuel mass flow rate based on air-fuel ratio
        fuel_mass_flow = air_mass_flow / conditions.air_fuel_ratio  # kg/s
        
        return air_mass_flow, fuel_mass_flow
    
    def calculate_combustion_parameters(self, conditions: OperatingConditions,
                                      air_mass_flow: float, fuel_mass_flow: float) -> Dict[str, float]:
        """
        Calculate combustion-related parameters
        
        Args:
            conditions (OperatingConditions): Operating conditions
            air_mass_flow (float): Air mass flow rate (kg/s)
            fuel_mass_flow (float): Fuel mass flow rate (kg/s)
            
        Returns:
            dict: Combustion parameters
        """
        fuel_props = self.fuel_properties[conditions.fuel_type]
        
        # Energy release rate
        energy_release_rate = fuel_mass_flow * fuel_props['heating_value'] * 1000  # W (kJ/kg to J/kg)
        
        # Effective energy after combustion efficiency
        effective_energy_rate = energy_release_rate * self.constants['combustion_efficiency']
        
        # Estimate combustion temperature (simplified)
        # This is a very simplified model - real combustion analysis is much more complex
        adiabatic_flame_temp = 2200 + conditions.ambient_temp  # K (rough estimate)
        
        # Heat transfer losses
        heat_transfer_factor = self.constants['heat_transfer_factor']
        net_energy_rate = effective_energy_rate * heat_transfer_factor
        
        return {
            'energy_release_rate': energy_release_rate,
            'effective_energy_rate': effective_energy_rate,
            'net_energy_rate': net_energy_rate,
            'adiabatic_flame_temp': adiabatic_flame_temp,
            'total_mass_flow': air_mass_flow + fuel_mass_flow
        }
    
    def calculate_exhaust_velocity(self, conditions: OperatingConditions,
                                 combustion_params: Dict[str, float]) -> float:
        """
        Calculate exhaust velocity based on energy conversion
        
        Args:
            conditions (OperatingConditions): Operating conditions
            combustion_params (dict): Combustion parameters
            
        Returns:
            float: Exhaust velocity in m/s
        """
        # Available kinetic energy per unit mass flow
        if combustion_params['total_mass_flow'] > 0:
            specific_energy = (combustion_params['net_energy_rate'] / 
                             combustion_params['total_mass_flow'])  # J/kg
        else:
            specific_energy = 0
        
        # Convert to exhaust velocity using kinetic energy relationship
        # v = sqrt(2 * specific_energy * exhaust_efficiency)
        exhaust_velocity = math.sqrt(2 * specific_energy * self.constants['exhaust_efficiency'])
        
        # Limit to reasonable values (speed of sound at combustion temperature is upper limit)
        max_velocity = math.sqrt(self.constants['gamma'] * self.constants['R'] * 
                               combustion_params['adiabatic_flame_temp'])
        exhaust_velocity = min(exhaust_velocity, max_velocity * 0.8)  # Subsonic limit
        
        return exhaust_velocity
    
    def calculate_thrust(self, air_mass_flow: float, fuel_mass_flow: float, 
                        exhaust_velocity: float, conditions: OperatingConditions,
                        geometry: EngineGeometry) -> float:
        """
        Calculate thrust using momentum theory with corrections
        
        Args:
            air_mass_flow (float): Air mass flow rate (kg/s)
            fuel_mass_flow (float): Fuel mass flow rate (kg/s)
            exhaust_velocity (float): Exhaust velocity (m/s)
            conditions (OperatingConditions): Operating conditions
            geometry (EngineGeometry): Engine geometry
            
        Returns:
            float: Total thrust in N
        """
        # Total mass flow
        total_mass_flow = air_mass_flow + fuel_mass_flow
        
        # Momentum thrust (primary component)
        momentum_thrust = total_mass_flow * exhaust_velocity
        
        # Pressure thrust (secondary component for unchoked flow)
        # This is simplified - assumes some expansion occurs
        pressure_pa = conditions.ambient_pressure * 1000
        exhaust_area_m2 = geometry.exhaust_area / 10000
        
        # Estimate pressure difference (very simplified)
        pressure_ratio = min(1.2, exhaust_velocity / 300)  # Empirical relationship
        pressure_diff = pressure_pa * (pressure_ratio - 1)
        pressure_thrust = pressure_diff * exhaust_area_m2
        
        # Total thrust
        total_thrust = momentum_thrust + pressure_thrust
        
        return max(0, total_thrust)  # Ensure non-negative
    
    def calculate_performance_metrics(self, thrust: float, fuel_mass_flow: float, 
                                    exhaust_velocity: float, combustion_params: Dict[str, float],
                                    conditions: OperatingConditions) -> Dict[str, float]:
        """
        Calculate additional performance metrics
        
        Args:
            thrust (float): Thrust in N
            fuel_mass_flow (float): Fuel mass flow rate (kg/s)
            exhaust_velocity (float): Exhaust velocity (m/s)
            combustion_params (dict): Combustion parameters
            conditions (OperatingConditions): Operating conditions
            
        Returns:
            dict: Performance metrics dictionary
        """
        # Specific impulse
        if fuel_mass_flow > 0:
            specific_impulse = thrust / (fuel_mass_flow * self.constants['g'])
        else:
            specific_impulse = 0
        
        # Jet power (kinetic power of exhaust)
        jet_power = 0.5 * combustion_params['total_mass_flow'] * exhaust_velocity**2 / 1000  # kW
        
        # Propulsive power (thrust power)
        # For static conditions, this is zero, so we use a fraction of jet power
        propulsive_power = jet_power * 0.5  # Rough estimate for propulsive efficiency
        
        # Thermal efficiency
        fuel_power = combustion_params['energy_release_rate'] / 1000  # kW
        if fuel_power > 0:
            thermal_efficiency = (propulsive_power / fuel_power) * 100
        else:
            thermal_efficiency = 0
        
        # Specific fuel consumption
        if propulsive_power > 0:
            sfc = fuel_mass_flow * 3600 / propulsive_power  # kg/kW·h
        else:
            sfc = float('inf')
        
        return {
            'specific_impulse': specific_impulse,
            'jet_power': jet_power,
            'propulsive_power': propulsive_power,
            'thermal_efficiency': thermal_efficiency,
            'specific_fuel_consumption': sfc
        }
    
    def run_complete_analysis(self, geometry: EngineGeometry, valves: ValveSystem,
                             conditions: OperatingConditions) -> PerformanceResults:
        """
        Run complete performance analysis
        
        This is the main method that orchestrates all calculations to produce
        a complete set of performance results.
        
        Args:
            geometry (EngineGeometry): Engine geometry parameters
            valves (ValveSystem): Valve system parameters
            conditions (OperatingConditions): Operating conditions
            
        Returns:
            PerformanceResults: Complete set of performance results
        """
        try:
            # Step 1: Calculate geometry parameters
            geom_params = self.calculate_geometry_parameters(geometry)
            
            # Step 2: Calculate operating frequency
            frequency = self.calculate_operating_frequency(geometry, conditions)
            
            # Step 3: Calculate mass flows
            air_mass_flow, fuel_mass_flow = self.calculate_mass_flows(
                geometry, valves, conditions, frequency)
            
            # Step 4: Calculate combustion parameters
            combustion_params = self.calculate_combustion_parameters(
                conditions, air_mass_flow, fuel_mass_flow)
            
            # Step 5: Calculate exhaust velocity
            exhaust_velocity = self.calculate_exhaust_velocity(conditions, combustion_params)
            
            # Step 6: Calculate thrust
            thrust = self.calculate_thrust(
                air_mass_flow, fuel_mass_flow, exhaust_velocity, conditions, geometry)
            
            # Step 7: Calculate performance metrics
            performance_metrics = self.calculate_performance_metrics(
                thrust, fuel_mass_flow, exhaust_velocity, combustion_params, conditions)
            
            # Create and return results
            results = PerformanceResults(
                # Geometry-derived
                combustion_volume=geom_params['combustion_volume'],
                intake_area=geom_params['intake_area'],
                exhaust_area=geom_params['exhaust_area'],
                
                # Operating parameters
                frequency=frequency,
                air_mass_flow=air_mass_flow,
                fuel_mass_flow=fuel_mass_flow,
                exhaust_velocity=exhaust_velocity,
                
                # Performance metrics
                thrust=thrust,
                specific_impulse=performance_metrics['specific_impulse'],
                power=performance_metrics['propulsive_power'],
                thermal_efficiency=performance_metrics['thermal_efficiency'],
                specific_fuel_consumption=performance_metrics['specific_fuel_consumption']
            )
            
            return results
            
        except Exception as e:
            # Log error and return zero results rather than failing
            warnings.warn(f"Analysis failed: {str(e)}")
            return PerformanceResults(
                combustion_volume=0, intake_area=0, exhaust_area=0,
                frequency=0, air_mass_flow=0, fuel_mass_flow=0, exhaust_velocity=0,
                thrust=0, specific_impulse=0, power=0, thermal_efficiency=0,
                specific_fuel_consumption=float('inf')
            )


class OptimizationAnalyzer:
    """
    Optimization and sensitivity analysis tools
    
    This class provides tools for analyzing design trade-offs, performing
    parameter sweeps, and generating optimization recommendations.
    """
    
    def __init__(self, model: PulseJetModel):
        """
        Initialize optimization analyzer
        
        Args:
            model (PulseJetModel): Pulse jet model instance to use for analysis
        """
        self.model = model
    
    def parameter_sweep(self, base_geometry: EngineGeometry, base_valves: ValveSystem,
                       base_conditions: OperatingConditions, 
                       parameter_name: str, parameter_range: np.ndarray) -> Dict[str, List]:
        """
        Perform parameter sweep analysis
        
        Args:
            base_geometry (EngineGeometry): Base geometry configuration
            base_valves (ValveSystem): Base valve configuration
            base_conditions (OperatingConditions): Base operating conditions
            parameter_name (str): Name of parameter to sweep
            parameter_range (np.ndarray): Range of parameter values to test
            
        Returns:
            dict: Dictionary containing sweep results
        """
        results = {
            'parameter_values': parameter_range.tolist(),
            'thrust': [],
            'frequency': [],
            'specific_impulse': [],
            'thermal_efficiency': [],
            'power': [],
            'fuel_consumption': []
        }
        
        for param_value in parameter_range:
            try:
                # Create modified configuration
                if hasattr(base_geometry, parameter_name):
                    # Geometry parameter
                    geometry_dict = {
                        'combustion_chamber_length': base_geometry.combustion_chamber_length,
                        'combustion_chamber_diameter': base_geometry.combustion_chamber_diameter,
                        'intake_diameter': base_geometry.intake_diameter,
                        'exhaust_diameter': base_geometry.exhaust_diameter,
                        'exhaust_length': base_geometry.exhaust_length
                    }
                    geometry_dict[parameter_name] = param_value
                    geometry = EngineGeometry(**geometry_dict)
                    valves = base_valves
                    conditions = base_conditions
                    
                elif hasattr(base_valves, parameter_name):
                    # Valve parameter
                    valve_dict = {
                        'valve_type': base_valves.valve_type,
                        'num_valves': base_valves.num_valves,
                        'valve_area': base_valves.valve_area
                    }
                    valve_dict[parameter_name] = param_value
                    geometry = base_geometry
                    valves = ValveSystem(**valve_dict)
                    conditions = base_conditions
                    
                elif hasattr(base_conditions, parameter_name):
                    # Operating condition parameter
                    condition_dict = {
                        'fuel_type': base_conditions.fuel_type,
                        'air_fuel_ratio': base_conditions.air_fuel_ratio,
                        'ambient_pressure': base_conditions.ambient_pressure,
                        'ambient_temp': base_conditions.ambient_temp
                    }
                    condition_dict[parameter_name] = param_value
                    geometry = base_geometry
                    valves = base_valves
                    conditions = OperatingConditions(**condition_dict)
                    
                else:
                    raise ValueError(f"Unknown parameter: {parameter_name}")
                
                # Run analysis
                performance = self.model.run_complete_analysis(geometry, valves, conditions)
                
                # Store results
                results['thrust'].append(performance.thrust)
                results['frequency'].append(performance.frequency)
                results['specific_impulse'].append(performance.specific_impulse)
                results['thermal_efficiency'].append(performance.thermal_efficiency)
                results['power'].append(performance.power)
                results['fuel_consumption'].append(performance.fuel_consumption_rate)
                
            except Exception as e:
                # Handle errors gracefully by appending zeros
                warnings.warn(f"Error in parameter sweep at {parameter_name}={param_value}: {e}")
                results['thrust'].append(0)
                results['frequency'].append(0)
                results['specific_impulse'].append(0)
                results['thermal_efficiency'].append(0)
                results['power'].append(0)
                results['fuel_consumption'].append(0)
        
        return results
    
    def multi_parameter_optimization(self, base_geometry: EngineGeometry, 
                                   base_valves: ValveSystem, base_conditions: OperatingConditions,
                                   parameters: Dict[str, Tuple[float, float]], 
                                   objective: str = 'thrust') -> Dict[str, Any]:
        """
        Perform multi-parameter optimization using grid search
        
        Args:
            base_geometry (EngineGeometry): Base geometry configuration
            base_valves (ValveSystem): Base valve configuration
            base_conditions (OperatingConditions): Base operating conditions
            parameters (dict): Dictionary of parameter names and their (min, max) ranges
            objective (str): Objective function ('thrust', 'efficiency', 'specific_impulse')
            
        Returns:
            dict: Optimization results including best configuration
        """
        best_value = 0 if objective != 'specific_fuel_consumption' else float('inf')
        best_config = None
        all_results = []
        
        # Simple grid search (for demonstration - real optimization would use better algorithms)
        grid_points = 5  # Points per parameter
        
        # Generate parameter combinations
        param_names = list(parameters.keys())
        param_ranges = []
        
        for param_name in param_names:
            min_val, max_val = parameters[param_name]
            param_ranges.append(np.linspace(min_val, max_val, grid_points))
        
        # Evaluate all combinations
        total_combinations = grid_points ** len(param_names)
        evaluated = 0
        
        def evaluate_combination(param_values):
            nonlocal best_value, best_config
            
            try:
                # Create configuration with modified parameters
                geometry = base_geometry
                valves = base_valves
                conditions = base_conditions
                
                # Apply parameter changes
                for i, param_name in enumerate(param_names):
                    param_value = param_values[i]
                    
                    if hasattr(base_geometry, param_name):
                        geometry_dict = {
                            'combustion_chamber_length': geometry.combustion_chamber_length,
                            'combustion_chamber_diameter': geometry.combustion_chamber_diameter,
                            'intake_diameter': geometry.intake_diameter,
                            'exhaust_diameter': geometry.exhaust_diameter,
                            'exhaust_length': geometry.exhaust_length
                        }
                        geometry_dict[param_name] = param_value
                        geometry = EngineGeometry(**geometry_dict)
                
                # Run analysis
                performance = self.model.run_complete_analysis(geometry, valves, conditions)
                
                # Evaluate objective
                if objective == 'thrust':
                    obj_value = performance.thrust
                    is_better = obj_value > best_value
                elif objective == 'efficiency':
                    obj_value = performance.thermal_efficiency
                    is_better = obj_value > best_value
                elif objective == 'specific_impulse':
                    obj_value = performance.specific_impulse
                    is_better = obj_value > best_value
                elif objective == 'specific_fuel_consumption':
                    obj_value = performance.specific_fuel_consumption
                    is_better = obj_value < best_value
                else:
                    obj_value = performance.thrust
                    is_better = obj_value > best_value
                
                # Store result
                result = {
                    'parameters': dict(zip(param_names, param_values)),
                    'objective_value': obj_value,
                    'performance': performance
                }
                all_results.append(result)
                
                # Update best if improved
                if is_better:
                    best_value = obj_value
                    best_config = result
                    
            except Exception as e:
                warnings.warn(f"Error in optimization evaluation: {e}")
        
        # Generate and evaluate all combinations
        if len(param_names) == 1:
            for val in param_ranges[0]:
                evaluate_combination([val])
        elif len(param_names) == 2:
            for val1 in param_ranges[0]:
                for val2 in param_ranges[1]:
                    evaluate_combination([val1, val2])
        elif len(param_names) == 3:
            for val1 in param_ranges[0]:
                for val2 in param_ranges[1]:
                    for val3 in param_ranges[2]:
                        evaluate_combination([val1, val2, val3])
        
        return {
            'best_configuration': best_config,
            'best_value': best_value,
            'all_results': all_results,
            'objective': objective,
            'parameters_tested': param_names
        }
    
    def design_optimization_suggestions(self, geometry: EngineGeometry, 
                                      performance: PerformanceResults) -> Dict[str, str]:
        """
        Generate design optimization suggestions based on current performance
        
        Args:
            geometry (EngineGeometry): Current engine geometry
            performance (PerformanceResults): Current performance results
            
        Returns:
            dict: Dictionary of suggestion categories and recommendations
        """
        suggestions = {}
        
        # L/D ratio analysis
        ld_ratio = geometry.ld_ratio
        if ld_ratio < 2.0:
            suggestions['ld_ratio'] = f"L/D ratio is low ({ld_ratio:.1f}). Consider increasing chamber length for better combustion completeness."
        elif ld_ratio > 5.0:
            suggestions['ld_ratio'] = f"L/D ratio is high ({ld_ratio:.1f}). This may cause excessive heat transfer losses and weight."
        elif 2.0 <= ld_ratio <= 5.0:
            suggestions['ld_ratio'] = f"L/D ratio ({ld_ratio:.1f}) is in good range for pulse jets."
        
        # Frequency analysis
        if performance.frequency < 30:
            suggestions['frequency'] = "Low operating frequency may reduce power density. Consider shortening exhaust length."
        elif performance.frequency > 250:
            suggestions['frequency'] = "High operating frequency may cause structural stress and wear. Consider lengthening exhaust."
        elif 50 <= performance.frequency <= 150:
            suggestions['frequency'] = f"Operating frequency ({performance.frequency:.0f} Hz) is in optimal range."
        
        # Area ratio analysis
        area_ratio = geometry.area_ratio
        if area_ratio < 1.0:
            suggestions['area_ratio'] = "Exhaust area smaller than intake - this may restrict flow and reduce performance."
        elif area_ratio > 3.0:
            suggestions['area_ratio'] = "Very large exhaust/intake area ratio may affect resonance tuning."
        elif 1.2 <= area_ratio <= 2.5:
            suggestions['area_ratio'] = f"Area ratio ({area_ratio:.2f}) is well-balanced."
        
        # Efficiency analysis
        if performance.thermal_efficiency < 10:
            suggestions['efficiency'] = "Low thermal efficiency. Consider optimizing combustion chamber geometry and air-fuel mixing."
        elif performance.thermal_efficiency > 35:
            suggestions['efficiency'] = f"Excellent thermal efficiency ({performance.thermal_efficiency:.1f}%)!"
        elif 15 <= performance.thermal_efficiency <= 25:
            suggestions['efficiency'] = f"Thermal efficiency ({performance.thermal_efficiency:.1f}%) is typical for pulse jets."
        
        # Thrust-to-weight analysis
        if performance.thrust_to_weight_ratio < 2:
            suggestions['thrust_to_weight'] = "Low thrust-to-weight ratio. Consider increasing chamber diameter or optimizing valve area."
        elif performance.thrust_to_weight_ratio > 8:
            suggestions['thrust_to_weight'] = f"Excellent thrust-to-weight ratio ({performance.thrust_to_weight_ratio:.1f})!"
        
        # Specific impulse analysis
        if performance.specific_impulse < 80:
            suggestions['specific_impulse'] = "Low specific impulse indicates poor fuel efficiency. Optimize air-fuel ratio and combustion."
        elif performance.specific_impulse > 200:
            suggestions['specific_impulse'] = f"Outstanding specific impulse ({performance.specific_impulse:.0f} s)!"
        
        return suggestions
    
    def trade_off_analysis(self, geometry: EngineGeometry, valves: ValveSystem,
                          conditions: OperatingConditions) -> Dict[str, Dict]:
        """
        Analyze design trade-offs for key parameters
        
        Args:
            geometry (EngineGeometry): Engine geometry
            valves (ValveSystem): Valve system
            conditions (OperatingConditions): Operating conditions
            
        Returns:
            dict: Trade-off analysis results
        """
        trade_offs = {
            'exhaust_length': {
                'parameter': 'Exhaust Length',
                'increase_benefits': [
                    'Lower operating frequency',
                    'Better resonance tuning potential',
                    'Improved expansion efficiency'
                ],
                'increase_drawbacks': [
                    'Increased weight and complexity',
                    'Higher heat transfer losses',
                    'More difficult mounting and integration'
                ],
                'optimal_range': '2-4 times chamber diameter'
            },
            'chamber_diameter': {
                'parameter': 'Chamber Diameter',
                'increase_benefits': [
                    'Higher thrust potential',
                    'Better combustion volume',
                    'Improved mixing characteristics'
                ],
                'increase_drawbacks': [
                    'Increased weight',
                    'Higher fuel consumption',
                    'Larger frontal area'
                ],
                'optimal_range': 'L/D ratio of 2.5-4.5'
            },
            'valve_area': {
                'parameter': 'Valve Area',
                'increase_benefits': [
                    'Better engine breathing',
                    'Higher mass flow potential',
                    'Improved performance at high frequencies'
                ],
                'increase_drawbacks': [
                    'Structural complexity',
                    'Potential for valve flutter',
                    'Reduced pressure rise'
                ],
                'optimal_range': '80-150% of intake area'
            },
            'air_fuel_ratio': {
                'parameter': 'Air-Fuel Ratio',
                'increase_benefits': [
                    'Better fuel economy',
                    'Cleaner combustion',
                    'Lower emissions'
                ],
                'increase_drawbacks': [
                    'Reduced power output',
                    'Potential for misfire',
                    'Incomplete combustion'
                ],
                'optimal_range': 'Near stoichiometric ratio'
            }
        }
        
        return trade_offs
    
    def sensitivity_analysis(self, geometry: EngineGeometry, valves: ValveSystem,
                           conditions: OperatingConditions, 
                           parameters: List[str] = None) -> Dict[str, float]:
        """
        Perform sensitivity analysis to determine parameter importance
        
        Args:
            geometry (EngineGeometry): Base geometry
            valves (ValveSystem): Base valve system
            conditions (OperatingConditions): Base conditions
            parameters (list, optional): Parameters to analyze
            
        Returns:
            dict: Sensitivity coefficients for each parameter
        """
        if parameters is None:
            parameters = ['exhaust_length', 'combustion_chamber_diameter', 
                         'air_fuel_ratio', 'valve_area']
        
        # Get baseline performance
        baseline = self.model.run_complete_analysis(geometry, valves, conditions)
        baseline_thrust = baseline.thrust
        
        sensitivity = {}
        delta_percent = 0.01  # 1% change
        
        for param_name in parameters:
            try:
                # Get current parameter value
                if hasattr(geometry, param_name):
                    current_value = getattr(geometry, param_name)
                    obj = geometry
                elif hasattr(valves, param_name):
                    current_value = getattr(valves, param_name)
                    obj = valves
                elif hasattr(conditions, param_name):
                    current_value = getattr(conditions, param_name)
                    obj = conditions
                else:
                    continue
                
                # Calculate perturbed value
                delta_value = current_value * delta_percent
                perturbed_value = current_value + delta_value
                
                # Create perturbed configuration
                if obj == geometry:
                    geometry_dict = {
                        'combustion_chamber_length': geometry.combustion_chamber_length,
                        'combustion_chamber_diameter': geometry.combustion_chamber_diameter,
                        'intake_diameter': geometry.intake_diameter,
                        'exhaust_diameter': geometry.exhaust_diameter,
                        'exhaust_length': geometry.exhaust_length
                    }
                    geometry_dict[param_name] = perturbed_value
                    perturbed_geometry = EngineGeometry(**geometry_dict)
                    perturbed_valves = valves
                    perturbed_conditions = conditions
                elif obj == valves:
                    valve_dict = {
                        'valve_type': valves.valve_type,
                        'num_valves': valves.num_valves,
                        'valve_area': valves.valve_area
                    }
                    valve_dict[param_name] = perturbed_value
                    perturbed_geometry = geometry
                    perturbed_valves = ValveSystem(**valve_dict)
                    perturbed_conditions = conditions
                else:  # conditions
                    condition_dict = {
                        'fuel_type': conditions.fuel_type,
                        'air_fuel_ratio': conditions.air_fuel_ratio,
                        'ambient_pressure': conditions.ambient_pressure,
                        'ambient_temp': conditions.ambient_temp
                    }
                    condition_dict[param_name] = perturbed_value
                    perturbed_geometry = geometry
                    perturbed_valves = valves
                    perturbed_conditions = OperatingConditions(**condition_dict)
                
                # Run perturbed analysis
                perturbed_results = self.model.run_complete_analysis(
                    perturbed_geometry, perturbed_valves, perturbed_conditions)
                
                # Calculate sensitivity coefficient
                if baseline_thrust > 0:
                    thrust_change_percent = ((perturbed_results.thrust - baseline_thrust) / 
                                           baseline_thrust) * 100
                    sensitivity_coeff = thrust_change_percent / (delta_percent * 100)
                    sensitivity[param_name] = sensitivity_coeff
                else:
                    sensitivity[param_name] = 0
                    
            except Exception as e:
                warnings.warn(f"Error in sensitivity analysis for {param_name}: {e}")
                sensitivity[param_name] = 0
        
        return sensitivity


# Utility functions for model validation and testing
def validate_model_inputs(geometry: EngineGeometry, valves: ValveSystem, 
                         conditions: OperatingConditions) -> Tuple[bool, List[str]]:
    """
    Validate model inputs for physical reasonableness
    
    Args:
        geometry (EngineGeometry): Engine geometry to validate
        valves (ValveSystem): Valve system to validate
        conditions (OperatingConditions): Operating conditions to validate
        
    Returns:
        tuple: (is_valid, list_of_errors)
    """
    errors = []
    
    # Geometry validation
    if geometry.ld_ratio < 0.5 or geometry.ld_ratio > 10:
        errors.append(f"L/D ratio ({geometry.ld_ratio:.1f}) is outside reasonable range (0.5-10)")
    
    if geometry.area_ratio < 0.5 or geometry.area_ratio > 5:
        errors.append(f"Area ratio ({geometry.area_ratio:.2f}) is outside reasonable range (0.5-5)")
    
    if geometry.intake_diameter >= geometry.combustion_chamber_diameter:
        errors.append("Intake diameter should be smaller than combustion chamber diameter")
    
    # Valve validation
    valve_to_intake_ratio = valves.valve_area / geometry.intake_area
    if valve_to_intake_ratio < 0.3 or valve_to_intake_ratio > 3:
        errors.append(f"Valve area ratio ({valve_to_intake_ratio:.2f}) is outside reasonable range (0.3-3)")
    
    # Operating conditions validation
    fuel_props = load_fuel_properties()
    if conditions.fuel_type in fuel_props:
        stoich_ratio = fuel_props[conditions.fuel_type]['stoich_ratio']
        if conditions.air_fuel_ratio < stoich_ratio * 0.7 or conditions.air_fuel_ratio > stoich_ratio * 1.5:
            errors.append(f"Air-fuel ratio ({conditions.air_fuel_ratio:.1f}) is far from stoichiometric ({stoich_ratio:.1f})")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def create_performance_summary(results: PerformanceResults) -> str:
    """
    Create a formatted performance summary string
    
    Args:
        results (PerformanceResults): Performance results to summarize
        
    Returns:
        str: Formatted summary string
    """
    summary = f"""
Pulse Jet Performance Summary
============================

Thrust Performance:
  • Thrust: {results.thrust:.1f} N ({results.thrust/9.81:.1f} kgf)
  • Specific Impulse: {results.specific_impulse:.0f} s
  • Thrust-to-Weight: {results.thrust_to_weight_ratio:.1f}

Operating Characteristics:
  • Frequency: {results.frequency:.0f} Hz
  • Air Mass Flow: {results.air_mass_flow:.3f} kg/s
  • Fuel Mass Flow: {results.fuel_mass_flow:.4f} kg/s
  • Exhaust Velocity: {results.exhaust_velocity:.0f} m/s

Efficiency Metrics:
  • Thermal Efficiency: {results.thermal_efficiency:.1f}%
  • Power Output: {results.power:.1f} kW
  • Fuel Consumption: {results.fuel_consumption_rate:.2f} kg/h
  • Specific Fuel Consumption: {results.specific_fuel_consumption:.2f} kg/kW·h

Engine Geometry:
  • Combustion Volume: {results.combustion_volume:.2f} L
  • Intake Area: {results.intake_area:.1f} cm²
  • Exhaust Area: {results.exhaust_area:.1f} cm²
"""
    return summary


# Export all public classes and functions
__all__ = [
    'EngineGeometry',
    'ValveSystem', 
    'OperatingConditions',
    'PerformanceResults',
    'PulseJetModel',
    'OptimizationAnalyzer',
    'validate_model_inputs',
    'create_performance_summary'
]
