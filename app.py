#!/usr/bin/env python3
"""
Pulse Jet Engine Design & Performance Modeler
Main Streamlit Application

A comprehensive tool for modeling and analyzing pulse jet engine designs.
This application provides physics-based models for performance prediction,
optimization tools, and validation utilities.

Author: Pulse Jet Modeler Contributors
License: MIT
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import json
import yaml
from pathlib import Path
import sys
import traceback
from datetime import datetime

# Add src to path for imports
sys.path.append('src')

# Import our custom modules
try:
    from src.pulse_jet_models import (
        PulseJetModel, EngineGeometry, ValveSystem, 
        OperatingConditions, OptimizationAnalyzer
    )
    from src.utils import (
        load_config, load_fuel_properties, save_configuration,
        load_configuration, export_results_to_csv, format_parameter_value,
        calculate_design_score, generate_design_report, create_comparison_table
    )
    from src.validators import (
        validate_all_parameters, show_validation_results,
        sanitize_input
    )
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please ensure all required modules are installed and in the correct location.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Pulse Jet Design Modeler",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-username/pulse-jet-modeler',
        'Report a bug': 'https://github.com/your-username/pulse-jet-modeler/issues',
        'About': "Pulse Jet Engine Design & Performance Modeler v1.0.0"
    }
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #FF4B4B;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'model' not in st.session_state:
        st.session_state.model = PulseJetModel()
    
    if 'saved_designs' not in st.session_state:
        st.session_state.saved_designs = []
    
    if 'current_config' not in st.session_state:
        st.session_state.current_config = None
    
    if 'validation_passed' not in st.session_state:
        st.session_state.validation_passed = True

def load_sample_configurations():
    """Load sample configurations from file"""
    try:
        config_file = Path('data/sample_configurations.json')
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)['configurations']
        else:
            return []
    except Exception as e:
        st.warning(f"Could not load sample configurations: {e}")
        return []

def create_sidebar_inputs():
    """Create sidebar input controls"""
    st.sidebar.markdown("## 🎛️ Design Parameters")
    
    # Load sample configurations
    sample_configs = load_sample_configurations()
    
    # Configuration selector
    if sample_configs:
        st.sidebar.markdown("### 📁 Load Sample Design")
        config_names = ["Custom"] + [config['name'] for config in sample_configs]
        selected_config = st.sidebar.selectbox("Sample Configurations", config_names)
        
        if selected_config != "Custom":
            # Load selected configuration
            config = next(c for c in sample_configs if c['name'] == selected_config)
            st.sidebar.info(f"Loaded: {config['description']}")
            
            # Set default values from configuration
            default_values = config
        else:
            default_values = None
    else:
        default_values = None
    
    # Engine geometry section
    st.sidebar.markdown("### 🔧 Engine Geometry")
    
    # Get default values or use standard defaults
    if default_values:
        geom = default_values['geometry']
        combustion_chamber_length = st.sidebar.slider(
            "Combustion Chamber Length (cm)", 10, 100, geom['combustion_chamber_length']
        )
        combustion_chamber_diameter = st.sidebar.slider(
            "Combustion Chamber Diameter (cm)", 5, 30, geom['combustion_chamber_diameter']
        )
        intake_diameter = st.sidebar.slider(
            "Intake Diameter (cm)", 2, 15, geom['intake_diameter']
        )
        exhaust_diameter = st.sidebar.slider(
            "Exhaust Diameter (cm)", 3, 20, geom['exhaust_diameter']
        )
        exhaust_length = st.sidebar.slider(
            "Exhaust Length (cm)", 20, 200, geom['exhaust_length']
        )
    else:
        combustion_chamber_length = st.sidebar.slider("Combustion Chamber Length (cm)", 10, 100, 50)
        combustion_chamber_diameter = st.sidebar.slider("Combustion Chamber Diameter (cm)", 5, 30, 15)
        intake_diameter = st.sidebar.slider("Intake Diameter (cm)", 2, 15, 8)
        exhaust_diameter = st.sidebar.slider("Exhaust Diameter (cm)", 3, 20, 10)
        exhaust_length = st.sidebar.slider("Exhaust Length (cm)", 20, 200, 80)
    
    # Valve system section
    st.sidebar.markdown("### ⚙️ Valve System")
    
    if default_values:
        valve_defaults = default_values['valves']
        valve_type = st.sidebar.selectbox(
            "Valve Type", ["Reed Valves", "Flapper Valves", "Rotary Valves"], 
            index=["Reed Valves", "Flapper Valves", "Rotary Valves"].index(valve_defaults['valve_type'])
        )
        num_valves = st.sidebar.slider("Number of Valves", 1, 12, valve_defaults['num_valves'])
        valve_area = st.sidebar.slider("Total Valve Area (cm²)", 5, 50, valve_defaults['valve_area'])
    else:
        valve_type = st.sidebar.selectbox("Valve Type", ["Reed Valves", "Flapper Valves", "Rotary Valves"])
        num_valves = st.sidebar.slider("Number of Valves", 1, 12, 4)
        valve_area = st.sidebar.slider("Total Valve Area (cm²)", 5, 50, 20)
    
    # Operating conditions section
    st.sidebar.markdown("### 🌡️ Operating Conditions")
    
    if default_values:
        op_defaults = default_values['operating']
        fuel_type = st.sidebar.selectbox(
            "Fuel Type", ["Gasoline", "Propane", "Hydrogen", "Kerosene"],
            index=["Gasoline", "Propane", "Hydrogen", "Kerosene"].index(op_defaults['fuel_type'])
        )
        # FIX: Convert to float to match step parameter
        air_fuel_ratio = st.sidebar.slider("Air-Fuel Ratio", 10.0, 20.0, float(op_defaults['air_fuel_ratio']), 0.1)
        # FIX: Convert to float to match step parameter  
        ambient_pressure = st.sidebar.slider("Ambient Pressure (kPa)", 80.0, 120.0, float(op_defaults['ambient_pressure']), 0.1)
        ambient_temp = st.sidebar.slider("Ambient Temperature (°C)", -20, 50, op_defaults['ambient_temp'])
    else:
        fuel_type = st.sidebar.selectbox("Fuel Type", ["Gasoline", "Propane", "Hydrogen", "Kerosene"])
        # FIX: All parameters should be float when using float step
        air_fuel_ratio = st.sidebar.slider("Air-Fuel Ratio", 10.0, 20.0, 14.7, 0.1)
        ambient_pressure = st.sidebar.slider("Ambient Pressure (kPa)", 80.0, 120.0, 101.3, 0.1)
        ambient_temp = st.sidebar.slider("Ambient Temperature (°C)", -20, 50, 20)
    
    return {
        'geometry': {
            'combustion_chamber_length': combustion_chamber_length,
            'combustion_chamber_diameter': combustion_chamber_diameter,
            'intake_diameter': intake_diameter,
            'exhaust_diameter': exhaust_diameter,
            'exhaust_length': exhaust_length
        },
        'valves': {
            'valve_type': valve_type,
            'num_valves': num_valves,
            'valve_area': valve_area
        },
        'operating': {
            'fuel_type': fuel_type,
            'air_fuel_ratio': air_fuel_ratio,
            'ambient_pressure': ambient_pressure,
            'ambient_temp': ambient_temp
        }
    }

def run_performance_analysis(params):
    """Run complete performance analysis"""
    try:
        # Create data objects
        geometry = EngineGeometry(
            combustion_chamber_length=params['geometry']['combustion_chamber_length'],
            combustion_chamber_diameter=params['geometry']['combustion_chamber_diameter'],
            intake_diameter=params['geometry']['intake_diameter'],
            exhaust_diameter=params['geometry']['exhaust_diameter'],
            exhaust_length=params['geometry']['exhaust_length']
        )
        
        valves = ValveSystem(
            valve_type=params['valves']['valve_type'],
            num_valves=params['valves']['num_valves'],
            valve_area=params['valves']['valve_area']
        )
        
        conditions = OperatingConditions(
            fuel_type=params['operating']['fuel_type'],
            air_fuel_ratio=params['operating']['air_fuel_ratio'],
            ambient_pressure=params['operating']['ambient_pressure'],
            ambient_temp=params['operating']['ambient_temp']
        )
        
        # Run analysis
        results = st.session_state.model.run_complete_analysis(geometry, valves, conditions)
        
        return results, geometry, valves, conditions
        
    except Exception as e:
        st.error(f"Error in performance analysis: {str(e)}")
        st.error(f"Traceback: {traceback.format_exc()}")
        return None, None, None, None

def display_performance_metrics(results):
    """Display performance metrics in an organized layout"""
    if results is None:
        st.error("No results to display")
        return
    
    st.markdown("## 📊 Performance Results")
    
    # Main metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Thrust", 
            f"{results.thrust:.1f} N",
            delta=f"{results.thrust/9.81:.1f} kgf",
            help="Total thrust produced by the engine"
        )
    
    with col2:
        st.metric(
            "Frequency", 
            f"{results.frequency:.0f} Hz",
            help="Operating frequency based on resonance tuning"
        )
    
    with col3:
        st.metric(
            "Specific Impulse", 
            f"{results.specific_impulse:.0f} s",
            help="Fuel efficiency measure - higher is better"
        )
    
    with col4:
        st.metric(
            "Power Output", 
            f"{results.power:.1f} kW",
            help="Estimated power output of the engine"
        )
    
    # Secondary metrics
    col5, col6, col7, col8 = st.columns(4)
    
    with col5:
        st.metric(
            "Thermal Efficiency",
            f"{results.thermal_efficiency:.1f}%",
            help="Efficiency of fuel energy conversion"
        )
    
    with col6:
        st.metric(
            "Air Mass Flow",
            f"{results.air_mass_flow:.3f} kg/s",
            help="Air mass flow rate through the engine"
        )
    
    with col7:
        st.metric(
            "Fuel Mass Flow",
            f"{results.fuel_mass_flow:.4f} kg/s",
            help="Fuel mass flow rate"
        )
    
    with col8:
        st.metric(
            "Exhaust Velocity",
            f"{results.exhaust_velocity:.0f} m/s",
            help="Exhaust gas velocity"
        )

def create_performance_plots(results, geometry, params):
    """Create performance analysis plots"""
    if results is None:
        return
    
    st.markdown("## 📈 Performance Analysis")
    
    # Create tabs for different plot types
    plot_tab1, plot_tab2, plot_tab3 = st.tabs(["Frequency Analysis", "Thrust Analysis", "Efficiency Analysis"])
    
    with plot_tab1:
        # Frequency vs exhaust length plot
        exhaust_lengths = np.linspace(20, 200, 50)
        frequencies = []
        
        for length in exhaust_lengths:
            # Calculate frequency for each length
            temp_geometry = EngineGeometry(
                combustion_chamber_length=geometry.combustion_chamber_length,
                combustion_chamber_diameter=geometry.combustion_chamber_diameter,
                intake_diameter=geometry.intake_diameter,
                exhaust_diameter=geometry.exhaust_diameter,
                exhaust_length=length
            )
            temp_conditions = OperatingConditions(
                fuel_type=params['operating']['fuel_type'],
                air_fuel_ratio=params['operating']['air_fuel_ratio'],
                ambient_pressure=params['operating']['ambient_pressure'],
                ambient_temp=params['operating']['ambient_temp']
            )
            freq = st.session_state.model.calculate_operating_frequency(temp_geometry, temp_conditions)
            frequencies.append(freq)
        
        fig_freq = go.Figure()
        fig_freq.add_trace(go.Scatter(
            x=exhaust_lengths, y=frequencies, 
            mode='lines', name='Frequency',
            line=dict(color='#FF4B4B', width=3)
        ))
        fig_freq.add_trace(go.Scatter(
            x=[geometry.exhaust_length], y=[results.frequency], 
            mode='markers', marker=dict(size=12, color='red'), 
            name='Current Design'
        ))
        fig_freq.update_layout(
            title="Operating Frequency vs Exhaust Length",
            xaxis_title="Exhaust Length (cm)",
            yaxis_title="Frequency (Hz)",
            template="plotly_white"
        )
        st.plotly_chart(fig_freq, use_container_width=True)
    
    with plot_tab2:
        # Thrust vs chamber diameter
        diameters = np.linspace(5, 30, 20)
        thrust_values = []
        
        for diameter in diameters:
            temp_geometry = EngineGeometry(
                combustion_chamber_length=geometry.combustion_chamber_length,
                combustion_chamber_diameter=diameter,
                intake_diameter=geometry.intake_diameter,
                exhaust_diameter=geometry.exhaust_diameter,
                exhaust_length=geometry.exhaust_length
            )
            temp_valves = ValveSystem(
                valve_type=params['valves']['valve_type'],
                num_valves=params['valves']['num_valves'],
                valve_area=params['valves']['valve_area']
            )
            temp_conditions = OperatingConditions(
                fuel_type=params['operating']['fuel_type'],
                air_fuel_ratio=params['operating']['air_fuel_ratio'],
                ambient_pressure=params['operating']['ambient_pressure'],
                ambient_temp=params['operating']['ambient_temp']
            )
            temp_results = st.session_state.model.run_complete_analysis(temp_geometry, temp_valves, temp_conditions)
            thrust_values.append(temp_results.thrust)
        
        fig_thrust = go.Figure()
        fig_thrust.add_trace(go.Scatter(
            x=diameters, y=thrust_values, 
            mode='lines', name='Thrust',
            line=dict(color='#00D4AA', width=3)
        ))
        fig_thrust.add_trace(go.Scatter(
            x=[geometry.combustion_chamber_diameter], y=[results.thrust], 
            mode='markers', marker=dict(size=12, color='green'), 
            name='Current Design'
        ))
        fig_thrust.update_layout(
            title="Thrust vs Combustion Chamber Diameter",
            xaxis_title="Chamber Diameter (cm)",
            yaxis_title="Thrust (N)",
            template="plotly_white"
        )
        st.plotly_chart(fig_thrust, use_container_width=True)
    
    with plot_tab3:
        # Efficiency analysis
        afr_range = np.linspace(10, 20, 20)
        efficiency_values = []
        
        for afr in afr_range:
            temp_conditions = OperatingConditions(
                fuel_type=params['operating']['fuel_type'],
                air_fuel_ratio=afr,
                ambient_pressure=params['operating']['ambient_pressure'],
                ambient_temp=params['operating']['ambient_temp']
            )
            temp_valves = ValveSystem(
                valve_type=params['valves']['valve_type'],
                num_valves=params['valves']['num_valves'],
                valve_area=params['valves']['valve_area']
            )
            temp_results = st.session_state.model.run_complete_analysis(geometry, temp_valves, temp_conditions)
            efficiency_values.append(temp_results.thermal_efficiency)
        
        fig_eff = go.Figure()
        fig_eff.add_trace(go.Scatter(
            x=afr_range, y=efficiency_values, 
            mode='lines', name='Thermal Efficiency',
            line=dict(color='#FFC107', width=3)
        ))
        fig_eff.add_trace(go.Scatter(
            x=[params['operating']['air_fuel_ratio']], y=[results.thermal_efficiency], 
            mode='markers', marker=dict(size=12, color='orange'), 
            name='Current Design'
        ))
        fig_eff.update_layout(
            title="Thermal Efficiency vs Air-Fuel Ratio",
            xaxis_title="Air-Fuel Ratio",
            yaxis_title="Thermal Efficiency (%)",
            template="plotly_white"
        )
        st.plotly_chart(fig_eff, use_container_width=True)

def create_design_summary(results, geometry, params):
    """Create design summary sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📋 Design Summary")
    
    if results is None:
        st.sidebar.error("No results available")
        return
    
    # Design score
    score = calculate_design_score({
        'thrust': results.thrust,
        'specific_impulse': results.specific_impulse,
        'thermal_efficiency': results.thermal_efficiency,
        'frequency': results.frequency
    })
    
    st.sidebar.metric("Design Score", f"{score:.1f}/100")
    
    # Key ratios
    ld_ratio = geometry.combustion_chamber_length / geometry.combustion_chamber_diameter
    area_ratio = results.exhaust_area / results.intake_area
    
    st.sidebar.markdown("### Key Ratios")
    st.sidebar.write(f"L/D Ratio: {ld_ratio:.1f}")
    st.sidebar.write(f"Area Ratio: {area_ratio:.2f}")
    st.sidebar.write(f"Combustion Volume: {results.combustion_volume:.2f} L")
    
    # Performance summary
    st.sidebar.markdown("### Performance Summary")
    st.sidebar.write(f"Thrust/Weight*: {results.thrust/50:.1f}")
    st.sidebar.write(f"Power/Weight*: {results.power/5:.1f} kW/kg")
    st.sidebar.write(f"Fuel Consumption: {results.fuel_mass_flow*3600:.2f} kg/h")
    st.sidebar.caption("*Assuming 50N engine weight")

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🚀 Pulse Jet Engine Design & Performance Modeler</h1>', 
                unsafe_allow_html=True)
    st.markdown("Model and analyze different pulse jet engine configurations with physics-based calculations")
    
    # Get input parameters from sidebar
    params = create_sidebar_inputs()
    
    # Validate inputs
    is_valid, errors = validate_all_parameters(
        params['geometry'], params['valves'], params['operating']
    )
    
    if not is_valid:
        st.error("⚠️ Parameter Validation Failed")
        for error in errors:
            st.error(f"• {error}")
        st.stop()
    
    # Run performance analysis
    with st.spinner("Running performance analysis..."):
        results, geometry, valves, conditions = run_performance_analysis(params)
    
    if results is None:
        st.error("Failed to complete analysis. Please check your parameters.")
        st.stop()
    
    # Display results
    display_performance_metrics(results)
    
    # Create performance plots
    create_performance_plots(results, geometry, params)
    
    # Design summary in sidebar
    create_design_summary(results, geometry, params)
    
    # Optimization and analysis tabs
    st.markdown("---")
    analysis_tab1, analysis_tab2, analysis_tab3, analysis_tab4 = st.tabs([
        "📊 Parameter Sweeps", "🎯 Optimization", "💾 Save/Load", "📄 Export"
    ])
    
    with analysis_tab1:
        st.markdown("### Parameter Sensitivity Analysis")
        
        param_to_analyze = st.selectbox(
            "Parameter to Analyze", 
            ["exhaust_length", "combustion_chamber_diameter", "air_fuel_ratio", "intake_diameter"]
        )
        
        if st.button("Run Parameter Sweep"):
            with st.spinner("Running parameter sweep..."):
                optimizer = OptimizationAnalyzer(st.session_state.model)
                
                # Define parameter range
                if param_to_analyze == "exhaust_length":
                    param_range = np.linspace(20, 200, 20)
                elif param_to_analyze == "combustion_chamber_diameter":
                    param_range = np.linspace(5, 30, 20)
                elif param_to_analyze == "air_fuel_ratio":
                    param_range = np.linspace(10, 20, 20)
                else:  # intake_diameter
                    param_range = np.linspace(2, 15, 20)
                
                sweep_results = optimizer.parameter_sweep(
                    geometry, valves, conditions, param_to_analyze, param_range
                )
                
                # Create sweep plot
                fig_sweep = make_subplots(specs=[[{"secondary_y": True}]])
                
                fig_sweep.add_trace(
                    go.Scatter(x=sweep_results['parameter_values'], y=sweep_results['thrust'], 
                             name="Thrust (N)", line=dict(color='red')), 
                    secondary_y=False
                )
                fig_sweep.add_trace(
                    go.Scatter(x=sweep_results['parameter_values'], y=sweep_results['frequency'], 
                             name="Frequency (Hz)", line=dict(color='blue')), 
                    secondary_y=True
                )
                
                fig_sweep.update_xaxes(title_text=f"{param_to_analyze.replace('_', ' ').title()}")
                fig_sweep.update_yaxes(title_text="Thrust (N)", secondary_y=False)
                fig_sweep.update_yaxes(title_text="Frequency (Hz)", secondary_y=True)
                fig_sweep.update_layout(title=f"Parameter Sweep: {param_to_analyze}")
                
                st.plotly_chart(fig_sweep, use_container_width=True)
    
    with analysis_tab2:
        st.markdown("### Design Optimization Suggestions")
        
        # Generate optimization suggestions
        optimizer = OptimizationAnalyzer(st.session_state.model)
        suggestions = optimizer.design_optimization_suggestions(geometry, results)
        
        if suggestions:
            for category, suggestion in suggestions.items():
                st.info(f"**{category.replace('_', ' ').title()}**: {suggestion}")
        else:
            st.success("✅ Your design parameters are well-balanced!")
        
        # Trade-offs analysis
        st.markdown("### Design Trade-offs")
        tradeoff_data = {
            "Design Aspect": [
                "Exhaust Length",
                "Chamber Diameter", 
                "Intake Area",
                "Operating Frequency"
            ],
            "Increase Benefits": [
                "Lower frequency, better resonance",
                "Higher thrust, more fuel flow",
                "Better breathing, higher mass flow",
                "Higher power density"
            ],
            "Increase Drawbacks": [
                "Heavier, more complex mounting",
                "Heavier, higher fuel consumption",
                "Larger frontal area, more drag",
                "Higher stress, shorter life"
            ]
        }
        st.dataframe(pd.DataFrame(tradeoff_data), use_container_width=True)
    
    with analysis_tab3:
        st.markdown("### Configuration Management")
        
        col_save, col_load = st.columns(2)
        
        with col_save:
            st.markdown("#### Save Current Design")
            config_name = st.text_input("Configuration Name", value=f"Design_{datetime.now().strftime('%Y%m%d_%H%M')}")
            
            if st.button("Save Configuration"):
                config_data = {
                    **params,
                    'timestamp': datetime.now().isoformat(),
                    'results': {
                        'thrust': results.thrust,
                        'frequency': results.frequency,
                        'specific_impulse': results.specific_impulse,
                        'thermal_efficiency': results.thermal_efficiency
                    }
                }
                
                if save_configuration(config_data, config_name):
                    st.success(f"✅ Configuration '{config_name}' saved successfully!")
                    st.session_state.saved_designs.append(config_data)
        
        with col_load:
            st.markdown("#### Load Saved Design")
            # This would load from saved_configs directory
            st.info("Load functionality available in full deployment")
    
    with analysis_tab4:
        st.markdown("### Export Results")
        
        col_export1, col_export2 = st.columns(2)
        
        with col_export1:
            if st.button("Download Results CSV"):
                results_dict = {
                    'thrust_N': results.thrust,
                    'frequency_Hz': results.frequency,
                    'specific_impulse_s': results.specific_impulse,
                    'power_kW': results.power,
                    'thermal_efficiency_percent': results.thermal_efficiency,
                    'air_mass_flow_kg_s': results.air_mass_flow,
                    'fuel_mass_flow_kg_s': results.fuel_mass_flow,
                    'exhaust_velocity_m_s': results.exhaust_velocity,
                    'combustion_volume_L': results.combustion_volume
                }
                
                csv_data = export_results_to_csv(results_dict)
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name=f"pulse_jet_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        with col_export2:
            if st.button("Generate Design Report"):
                report = generate_design_report(params['geometry'], {
                    'thrust': results.thrust,
                    'frequency': results.frequency,
                    'specific_impulse': results.specific_impulse,
                    'thermal_efficiency': results.thermal_efficiency,
                    'air_mass_flow': results.air_mass_flow,
                    'fuel_mass_flow': results.fuel_mass_flow,
                    'exhaust_velocity': results.exhaust_velocity
                }, suggestions if 'suggestions' in locals() else {})
                
                st.download_button(
                    label="Download Report",
                    data=report,
                    file_name=f"pulse_jet_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown"
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9em;">
    <p><strong>⚠️ Important Disclaimer:</strong> This is a simplified model for educational and preliminary design purposes. 
    Actual pulse jet performance depends on many additional factors including combustion dynamics, 
    heat transfer, materials, and manufacturing tolerances. Always consult detailed engineering 
    analysis and testing for final designs.</p>
    
    <p>🔬 <strong>Model Accuracy:</strong> Results are order-of-magnitude estimates. Use for comparative analysis and design trends.</p>
    
    <p>🚀 <strong>Version:</strong> Pulse Jet Modeler v1.0.0 | 
    <a href="https://github.com/your-username/pulse-jet-modeler" target="_blank">GitHub</a> | 
    <a href="https://github.com/your-username/pulse-jet-modeler/issues" target="_blank">Report Issues</a></p>
    </div>
    """, unsafe_allow_html=True)

def run_app():
    """Entry point for running the application"""
    try:
        main()
    except Exception as e:
        st.error("🚨 Application Error")
        st.error(f"An unexpected error occurred: {str(e)}")
        
        if st.checkbox("Show detailed error information"):
            st.code(traceback.format_exc())
        
        st.info("Please check your parameters and try again. If the problem persists, please report this issue.")

if __name__ == "__main__":
    run_app()
