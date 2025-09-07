#!/usr/bin/env python3
"""
Setup script for Pulse Jet Engine Design & Performance Modeler

A comprehensive Streamlit application for modeling and analyzing pulse jet engine designs.
This package provides physics-based models for performance prediction, optimization tools,
and validation utilities for pulse jet engines.
"""

import os
import sys
from pathlib import Path
from setuptools import setup, find_packages

# Ensure we're using Python 3.8+
if sys.version_info < (3, 8):
    raise RuntimeError("This package requires Python 3.8 or later")

# Read the contents of README file
def read_file(filename):
    """Read contents of a file"""
    here = Path(__file__).parent
    try:
        with open(here / filename, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""

# Get long description from README
long_description = read_file('README.md')

# Get version from package
def get_version():
    """Get version from package __init__.py"""
    here = Path(__file__).parent
    version_file = here / 'src' / '__init__.py'
    
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('__version__'):
                    # Extract version string
                    return line.split('=')[1].strip().strip('"').strip("'")
    
    # Fallback version
    return "1.0.0"

# Read requirements from requirements.txt
def get_requirements():
    """Get requirements from requirements.txt"""
    requirements = []
    req_file = Path(__file__).parent / 'requirements.txt'
    
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    requirements.append(line)
    
    return requirements

# Development requirements
dev_requirements = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'black>=22.0.0',
    'flake8>=5.0.0',
    'mypy>=1.0.0',
    'pre-commit>=2.20.0',
    'sphinx>=5.0.0',
    'sphinx-rtd-theme>=1.0.0',
    'twine>=4.0.0'
]

# Documentation requirements
docs_requirements = [
    'sphinx>=5.0.0',
    'sphinx-rtd-theme>=1.0.0',
    'myst-parser>=0.18.0',
    'sphinx-autoapi>=2.0.0'
]

# Testing requirements
test_requirements = [
    'pytest>=7.0.0',
    'pytest-cov>=4.0.0',
    'pytest-mock>=3.8.0',
    'hypothesis>=6.0.0'
]

setup(
    # Basic package information
    name="pulse-jet-modeler",
    version=get_version(),
    author="Pulse Jet Modeler Contributors",
    author_email="contributors@pulse-jet-modeler.org",
    maintainer="Pulse Jet Modeler Team",
    maintainer_email="maintainers@pulse-jet-modeler.org",
    
    # Description
    description="A Streamlit app for pulse jet engine design and performance modeling",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    # URLs
    url="https://github.com/your-username/pulse-jet-modeler",
    project_urls={
        "Homepage": "https://github.com/your-username/pulse-jet-modeler",
        "Documentation": "https://pulse-jet-modeler.readthedocs.io/",
        "Source Code": "https://github.com/your-username/pulse-jet-modeler",
        "Bug Tracker": "https://github.com/your-username/pulse-jet-modeler/issues",
        "Download": "https://pypi.org/project/pulse-jet-modeler/",
        "Changelog": "https://github.com/your-username/pulse-jet-modeler/blob/main/CHANGELOG.md"
    },
    
    # Package discovery
    packages=find_packages(include=['src', 'src.*']),
    package_dir={'': '.'},
    
    # Include non-Python files
    include_package_data=True,
    package_data={
        'src': ['*.yaml', '*.json'],
        '': [
            'data/*.json',
            'config.yaml',
            'README.md',
            'LICENSE',
            'CHANGELOG.md'
        ]
    },
    
    # Requirements
    python_requires=">=3.8",
    install_requires=get_requirements(),
    
    # Optional dependencies
    extras_require={
        'dev': dev_requirements,
        'docs': docs_requirements,
        'test': test_requirements,
        'all': dev_requirements + docs_requirements + test_requirements
    },
    
    # Entry points for command-line scripts
    entry_points={
        'console_scripts': [
            'pulse-jet-modeler=src.cli:main',
            'pulse-jet-app=src.app_launcher:launch_app',
        ],
    },
    
    # Classification
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        
        # Intended Audience
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        
        # Topic
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
        
        # License
        "License :: OSI Approved :: MIT License",
        
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3 :: Only",
        
        # Framework
        "Framework :: Streamlit",
        
        # Natural Language
        "Natural Language :: English",
        
        # Environment
        "Environment :: Web Environment",
        "Environment :: Console",
    ],
    
    # Keywords
    keywords=[
        "pulse-jet", "engine", "propulsion", "aerospace", "modeling", 
        "simulation", "streamlit", "engineering", "physics", "thermodynamics",
        "combustion", "performance", "optimization", "design", "analysis"
    ],
    
    # Licensing
    license="MIT",
    license_files=["LICENSE"],
    
    # Platform support
    platforms=["any"],
    
    # Zip safety
    zip_safe=False,
    
    # Additional metadata for modern packaging
    obsoletes_dist=[],
    provides_dist=["pulse-jet-modeler"],
)

# Post-installation setup
def post_install():
    """Perform post-installation setup"""
    import os
    from pathlib import Path
    
    # Create necessary directories
    directories = [
        'data',
        'saved_configs',
        'saved_configs/examples',
        'exports',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        # Create .gitkeep files for empty directories
        gitkeep_file = Path(directory) / '.gitkeep'
        if not gitkeep_file.exists():
            gitkeep_file.touch()
    
    print("✅ Post-installation setup completed!")
    print("📁 Created necessary directories")
    print("🚀 Ready to run: streamlit run app.py")

# Custom command for development setup
class DevelopmentSetup:
    """Custom setup for development environment"""
    
    @staticmethod
    def setup_dev_environment():
        """Set up development environment"""
        import subprocess
        import sys
        
        try:
            # Install development dependencies
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-e', '.[dev]'
            ])
            
            # Install pre-commit hooks
            subprocess.check_call(['pre-commit', 'install'])
            
            print("✅ Development environment setup completed!")
            print("🔧 Pre-commit hooks installed")
            print("📝 Run 'make test' to verify installation")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error setting up development environment: {e}")
            sys.exit(1)

# Custom command for data setup
class DataSetup:
    """Custom setup for application data"""
    
    @staticmethod
    def setup_sample_data():
        """Set up sample data and configurations"""
        import json
        from pathlib import Path
        
        # Create sample fuel properties if not exists
        fuel_properties_file = Path('data/fuel_properties.json')
        if not fuel_properties_file.exists():
            sample_fuel_data = {
                "Gasoline": {
                    "heating_value": 44.0,
                    "density": 0.75,
                    "stoich_ratio": 14.7,
                    "molecular_weight": 100,
                    "autoignition_temp": 280
                },
                "Propane": {
                    "heating_value": 46.4,
                    "density": 0.51,
                    "stoich_ratio": 15.7,
                    "molecular_weight": 44,
                    "autoignition_temp": 470
                }
            }
            
            with open(fuel_properties_file, 'w') as f:
                json.dump(sample_fuel_data, f, indent=2)
        
        print("✅ Sample data setup completed!")

if __name__ == "__main__":
    # Check if this is being run for post-installation setup
    if len(sys.argv) > 1 and sys.argv[1] == 'post_install':
        post_install()
    elif len(sys.argv) > 1 and sys.argv[1] == 'dev_setup':
        DevelopmentSetup.setup_dev_environment()
    elif len(sys.argv) > 1 and sys.argv[1] == 'data_setup':
        DataSetup.setup_sample_data()
    else:
        # Normal setup.py execution
        print("🚀 Installing Pulse Jet Modeler...")
        print("📦 This may take a moment...")
