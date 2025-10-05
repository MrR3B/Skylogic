# Enhanced Aviation Dashboard

A real-time air quality and aviation safety monit## Files

- `enhanced_aviation_dashboard.R`: Main dashboard application with ML integration
- `simple_ml_predictor.py`: ML prediction service (85.2% R² accuracy models)
- `enhanced_aviation_ml.py`: Original ML training system 
- `forecasting_system.py`: 48-hour prediction system
- `air_quality_flight_safety_models.pkl`: Trained ML models
- `data/`: Ground truth data from 3 Oman cities (72K+ records)
- `merra2_data/`: NASA MERRA-2 satellite data filesystem for Oman using NASA satellite data.

## Features

- **🤖 ML-Powered Predictions**: Real trained models with 85.2% R² accuracy for PM2.5
- **Real-time Air Quality Monitoring**: PM2.5, PM10, AQI calculations using EPA standards
- **Aviation Safety Metrics**: Visibility, flight safety scores, turbulence risk assessment
- **Interactive Timeline**: Hour-by-hour ML prediction visualization with animation controls
- **3 Real Oman Locations**: Muscat, Salalah, Musandam (matching your actual data files)
- **48-Hour Forecasting**: Extended ML-based predictive modeling for proactive safety management
- **NASA Integration**: MERRA-2 satellite data processing with weather-pollution correlations

## Quick Start

### Method 1: RStudio (Recommended)
1. Open RStudio
2. Open the file: `enhanced_aviation_dashboard.R`
3. Install required packages if prompted:
   ```r
   install.packages(c("shiny", "shinydashboard", "leaflet", "dplyr"))
   ```
4. Click "Run App" button or execute:
   ```r
   runApp(shinyApp(ui = ui, server = server))
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

## Usage

1. **Load Sample Data**: Click "Load Sample Data" to see your 3 Oman locations (Muscat, Salalah, Musandam) with 48-hour predictions
2. **Timeline Control**: Use the hour slider (0-47) to see conditions over 2 days
3. **Animation**: Click the play button to automatically cycle through 48 hours
4. **Upload Data**: Use "Browse..." to upload your own CSV file with columns: site, lat, lon, pm25, pm10
5. **View Types**: Switch between "Current Conditions", "1h", "6h", "12h", "24h", and "48h Forecast" modes

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

## Project Context

This dashboard is part of a NASA-focused project for predicting air pollution and dangerous sky conditions in Oman using satellite data and cloud computing. The system integrates your trained ML models achieving 85.2% R² accuracy for PM2.5 predictions with real-time dashboard visualization. The ML predictions now replace mathematical simulations, providing authentic forecasting based on your 72K+ data points from Muscat, Salalah, and Musandam.

## Troubleshooting

- **R not found**: Install R from https://cran.r-project.org/
- **Package errors**: Run `install.packages(c("shiny", "shinydashboard", "leaflet", "dplyr"))`
- **Port busy**: The app runs on port 3838 by default
- **Data not loading**: Check that CSV format matches requirements above

## Files

- `enhanced_aviation_dashboard.R`: Main dashboard application
- `enhanced_aviation_ml.py`: Machine learning models (85.2% R² accuracy)
- `forecasting_system.py`: 48-hour prediction system
- `data/`: Ground truth data from 3 Oman cities (72K+ records)
- `merra2_data/`: NASA MERRA-2 satellite data files