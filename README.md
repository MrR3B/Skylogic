<div align="center">
  <img src="Skylogic.PNG" alt="SkyLogic Logo" width="400"/>
</div>

# SkyLogic - Air Quality & Weather Forecasting System

🌍 **Comprehensive Air Quality and Weather Forecasting System** for Oman region, serving both **general public** and **aviation pilots** with ML-powered predictions and real-time environmental monitoring.

## 👥 Who Can Use SkyLogic?

- **🏠 General Public**: Get reliable air quality forecasts for health planning and outdoor activities
- **✈️ Aviation Pilots**: Access critical flight safety data, visibility conditions, and weather hazards
- **🏥 Health Professionals**: Monitor air pollution trends for respiratory health advisories
- **🏛️ Government Agencies**: Track environmental conditions for policy and emergency planning

[![GitHub](https://img.shields.io/badge/GitHub-SkyLogic-blue?logo=github)](https://github.com/MrR3B/Skylogic)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![R](https://img.shields.io/badge/R-Shiny-blue?logo=r)](https://shiny.rstudio.com/)
[![Python](https://img.shields.io/badge/Python-ML-yellow?logo=python)](https://python.org/)

## 🤖 Machine Learning & Data Processing

### 📡 NASA EarthData Integration
Our system processes **reliable, scientific-grade data** from NASA EarthData repositories:

1. **🛰️ Data Source**: NASA MERRA-2 (Modern-Era Retrospective analysis for Research and Applications)
2. **📊 Data Processing**: Raw satellite data cleaned and processed into structured CSV files
3. **🗺️ Geographic Coverage**: Three key Oman locations - Muscat, Salalah, Musandam
4. **📈 Data Volume**: 72,000+ processed data points spanning multiple years
5. **🔄 Update Frequency**: Regular data refreshing from NASA EarthData API

### 🎯 ML Model Training & Selection

**📋 Model Selection Process** (detailed in [Nasa_report.pdf](Nasa_report.pdf)):

- **Algorithm Comparison**: Tested Random Forest, Gradient Boosting, Neural Networks, and ensemble methods
- **Performance Metrics**: Achieved **85.2% R² accuracy** for PM2.5 and PM10 predictions
- **Cross-Validation**: Location-specific validation across Muscat, Salalah, Musandam
- **Feature Engineering**: Weather patterns, seasonal variations, dust storm indicators
- **Model Optimization**: Hyperparameter tuning for optimal forecasting performance

### 🌟 System Capabilities

- **🤖 AI-Powered Predictions**: Scientifically-trained ML models with 85.2% accuracy for PM2.5 & PM10
- **🛩️ Aviation Safety**: Flight visibility, turbulence risk, and safety score calculations
- **🌍 Weather Integration**: Real-time data fusion with OpenWeatherMap API
- **📊 Interactive Dashboard**: Modern R Shiny interface with real-time updates
- **🗺️ Multi-Location Coverage**: Comprehensive monitoring across Oman region
- **⏰ 48-Hour Forecasting**: Extended predictions for planning and safety management

## 📁 Essential Files

### 🎯 **Core Application**
- `enhanced_aviation_dashboard.R`: Main R Shiny dashboard application
- `simple_ml_predictor.py`: ML prediction interface (85.2% R² accuracy for PM2.5 & PM10)
- `enhanced_aviation_ml.py`: ML model training system with NASA data integration

### 🤖 **Machine Learning & Data Processing**
- `forecasting_system.py`: 48-hour sequential prediction system
- `datacollection.py`: NASA EarthData API integration utilities
- `dataset.py`: Data processing and CSV generation tools
- `netcdf4_TO_CSV.py`: NetCDF to CSV conversion for NASA MERRA-2 data

### 📊 **Data & Models**
- `data/`: Processed CSV files from NASA EarthData (72K+ records)
  - `Muscat_oman_weather_aod_pm2023-2025.csv`
  - `Salalah_oman_weather_aod_pm2023-2025.csv`
  - `Musandam_oman_weather_aod_pm2023-2025.csv`
- `merra2_data/`: Raw NASA MERRA-2 NetCDF4 satellite data files
- `requirements.txt`: Python package dependencies

### 📋 **Documentation**
- `Nasa_report.pdf`: **Technical report on ML model selection and NASA data processing**
- `README.md`: This comprehensive guide
- `ml_model_analysis.png`: ML performance visualization

## 🔬 Technical Specifications

### 📊 **Data Quality & Accuracy**
- **Data Source**: NASA MERRA-2 satellite data (scientific-grade reliability)
- **ML Performance**: 85.2% R² accuracy for PM2.5 & PM10 predictions
- **Processing Volume**: 72,000+ cleaned and validated data points
- **Geographic Coverage**: Three strategic Oman locations
- **Temporal Resolution**: Hourly data with 48-hour forecasting capability

### 🛠️ **Technical Features**
- **Real-time Monitoring**: PM2.5, PM10, AQI calculations using EPA standards
- **Aviation Metrics**: Visibility estimation, flight safety scoring, turbulence risk
- **Interactive Visualization**: Hour-by-hour ML prediction with animation controls
- **Data Integration**: NASA satellite data + OpenWeatherMap API fusion
- **Cross-Platform**: R Shiny web interface accessible via any modern browser

## 🚀 Quick Start Guide

### 📋 Prerequisites
1. **R Programming Language** (version 4.0+) - [Download from CRAN](https://cran.r-project.org/)
2. **Python** (version 3.8+) - [Download from Python.org](https://python.org/)
3. **RStudio** (recommended) - [Download from RStudio](https://www.rstudio.com/)

### 🛠️ Installation

#### Step 1: Install R Dependencies
```r
install.packages(c(
  "shiny", "shinydashboard", "leaflet", "dplyr", 
  "plotly", "DT", "reticulate", "httr", "jsonlite", "lubridate"
))
```

#### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### Step 3: Train ML Models (First Time Only)
```bash
python enhanced_aviation_ml.py
```

### 🎯 Running the Dashboard

#### Method 1: RStudio (Recommended for Beginners)
1. Open RStudio
2. Open the file: `enhanced_aviation_dashboard.R`
3. Click "Run App" button or execute:
   ```r
   source("enhanced_aviation_dashboard.R")
   ```

### Method 2: R Console
```r
library(shiny)
library(shinydashboard)
library(leaflet)
library(dplyr)
source("enhanced_aviation_dashboard.R")
runApp(shinyApp(ui = ui, server = server))
```

### Method 3: Command Line (if R is in PATH)
```bash
Rscript -e "library(shiny); library(shinydashboard); library(leaflet); library(dplyr); source('enhanced_aviation_dashboard.R'); runApp(shinyApp(ui = ui, server = server))"
```

## 🎯 Usage Guide

### 👥 **For General Public**
1. **🏠 Health Monitoring**: Check current air quality before outdoor activities
2. **📅 Planning**: Use 48-hour forecasts for weekend trips and events
3. **🚨 Health Alerts**: Monitor PM2.5 & PM10 levels with ML predictions if you have respiratory conditions
4. **🌆 Location Comparison**: Compare air quality across Muscat, Salalah, Musandam

### ✈️ **For Aviation Pilots**
1. **🛩️ Pre-flight Planning**: Check visibility conditions and dust storm risks
2. **🌤️ Weather Assessment**: Access integrated weather and air quality data
3. **⚠️ Safety Scoring**: Review flight safety scores based on atmospheric conditions
4. **📊 Trend Analysis**: Monitor 48-hour forecasts for flight scheduling

### 🖥️ **Dashboard Controls**
1. **Load Sample Data**: Click to view real NASA-processed data for 3 Oman locations
2. **Timeline Control**: Use hour slider (0-47) to explore 48-hour forecasts
3. **Animation Mode**: Auto-cycle through time periods for trend visualization
4. **Custom Data Upload**: Upload your own CSV files with air quality measurements
5. **View Modes**: Switch between current conditions and various forecast horizons
6. **Interactive Maps**: Click locations for detailed environmental data

## Data Format

When uploading custom data, ensure your CSV has these columns:
- `site`: Location name
- `lat`: Latitude
- `lon`: Longitude  
- `pm25`: PM2.5 concentration (µg/m³)
- `pm10`: PM10 concentration (µg/m³)
- `temperature`: Temperature (°C) [optional, defaults to 25°C]
- `humidity`: Humidity (%) [optional, defaults to 60%]
- `wind_speed`: Wind speed (m/s) [optional, defaults to 10 m/s]
- `dust`: Dust concentration (µg/m³) [optional, defaults to 50 µg/m³]

## Technical Details

- **AQI Calculation**: EPA standard formula
- **Flight Safety Score**: Weighted combination of PM2.5, PM10, visibility, wind conditions
- **Visibility Estimation**: Based on atmospheric particle concentrations
- **Color Coding**: Green (Good) → Yellow (Moderate) → Orange (Unhealthy) → Red (Hazardous)

## 🛰️ Project Background & NASA Data Pipeline

### 📊 Data Collection & Processing Pipeline

1. **🛰️ NASA EarthData Access**: 
   - Direct connection to NASA's Earth Observing System Data
   - MERRA-2 atmospheric reanalysis data (0.5° × 0.625° resolution)
   - Real-time and historical meteorological parameters

2. **🔄 Data Processing Workflow**:
   ```
   NASA EarthData → NetCDF4 Files → Python Processing → Cleaned CSV → ML Training
   ```

3. **📍 Location-Specific Processing**:
   - **Muscat** (23.5933°N, 58.2844°E): Capital region monitoring
   - **Salalah** (17.0387°N, 54.0914°E): Southern coastal conditions
   - **Musandam** (26.2041°N, 56.2606°E): Northern mountainous terrain

4. **🎯 Model Development Process**:
   - **Data Volume**: 72,000+ scientifically processed data points
   - **Training Period**: Multi-year historical data for robust learning
   - **Validation**: Cross-location testing for geographic generalization
   - **Performance**: 85.2% R² accuracy for both PM2.5 & PM10 achieved through rigorous testing

### 📖 Technical Documentation

**[📄 Nasa_report.pdf](Nasa_report.pdf)** - Comprehensive technical report covering:
- NASA EarthData integration methodology
- ML model selection and comparison process
- Performance benchmarks and validation results
- Scientific basis for forecasting algorithms

### 🎯 Real-World Applications

- **Public Health**: Air quality alerts and health advisories
- **Aviation Safety**: Flight planning and risk assessment
- **Environmental Monitoring**: Pollution trend analysis
- **Emergency Response**: Dust storm and hazardous condition warnings

## Troubleshooting

- **R not found**: Install R from https://cran.r-project.org/
- **Package errors**: Run `install.packages(c("shiny", "shinydashboard", "leaflet", "dplyr"))`
- **Port busy**: The app runs on port 3838 by default
- **Data not loading**: Check that CSV format matches requirements above

---

## 📞 **Support & Contact**

For technical questions about the ML models, NASA data processing, or dashboard functionality, refer to the comprehensive technical documentation in `Nasa_report.pdf`.

**🚀 Ready to explore Oman's air quality future? Launch the dashboard and start forecasting!**