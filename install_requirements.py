#!/usr/bin/env python3
"""
Python Dependencies Installer for Skylogic Dashboard
"""

import subprocess
import sys

def install_packages():
    """Install required Python packages"""
    packages = [
        'numpy>=1.21.0',
        'pandas>=1.3.0', 
        'scikit-learn>=1.0.0',
        'xgboost>=1.5.0',
        'joblib>=1.1.0',
        'requests>=2.25.0',
        'netCDF4>=1.5.8',
        'matplotlib>=3.3.4',
        'seaborn>=0.11.1'
    ]
    
    print("🚀 Installing Python packages for Skylogic...")
    
    for package in packages:
        print(f"📦 Installing {package}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    print("\n🎯 Installation complete!")
    print("Next steps:")
    print("1. Install R packages: install.packages(c('shiny', 'shinydashboard', 'leaflet', 'dplyr'))")
    print("2. Train ML models: python enhanced_aviation_ml.py")
    print("3. Run dashboard: shiny::runApp('enhanced_aviation_dashboard.R')")

if __name__ == "__main__":
    install_packages()