# GitHub Upload Guide for Aviation Safety Dashboard

## Quick Upload Steps

### 1. Initialize Git Repository
```powershell
cd "c:\RAFO\R"
git init
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. Add Files and Commit
```powershell
git add .
git commit -m "Initial commit: Aviation Safety Dashboard with Real-time Weather Forecasting"
```

### 3. Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "+" → "New repository"
3. Repository name: `aviation-safety-dashboard`
4. Description: "Real-time Aviation Safety Dashboard with Weather API Integration and ML Forecasting for Oman Airports"
5. Set to **Public**
6. **Don't** initialize with README
7. Click "Create repository"

### 4. Connect and Push
```powershell
git remote add origin https://github.com/YOUR_USERNAME/aviation-safety-dashboard.git
git branch -M main
git push -u origin main
```

## Files to Upload (Complete List)

### 🎯 Core Application Files

#### `enhanced_aviation_dashboard.R` (Main Dashboard)
- **Purpose**: Complete R Shiny dashboard application
- **Features**: 
  - Real-time weather data from OpenWeatherMap API
  - 48-hour forecasting with intelligent dust estimation
  - Interactive maps for Muscat, Salalah, Musandam airports
  - ML-powered air quality predictions
  - Flight safety risk assessments
- **Size**: ~500 lines of R code
- **Dependencies**: shiny, shinydashboard, leaflet, plotly, DT, reticulate

#### `enhanced_aviation_ml.py` (ML Model Training)
- **Purpose**: Train machine learning models locally
- **Features**:
  - Random Forest + Gradient Boosting ensemble
  - Location-specific model training
  - Performance validation and metrics
  - Creates `air_quality_flight_safety_models.pkl`
- **Size**: ~300 lines of Python code
- **Output**: Trained ML models for dashboard

#### `simple_ml_predictor.py` (ML Interface)
- **Purpose**: Python interface for R dashboard to use ML models
- **Features**:
  - Load trained models
  - Make predictions from R via reticulate
  - Handle missing model files gracefully
- **Size**: ~100 lines of Python code
- **Integration**: Called by R dashboard for predictions

### 📊 Sample Data Files

#### `sample.csv` (Training Data Sample)
- **Purpose**: Sample weather and air quality data for ML training
- **Content**: 72 hours of realistic data for all 3 airports
- **Columns**: site, lat, lon, date, pm25, pm10, temperature, humidity, wind_speed, dust
- **Usage**: Used by ML training script if real data unavailable

#### `data/` folder (Historical Data)
- **Files**: 
  - `Muscat_oman_weather_aod_pm2023-2025.csv`
  - `Salalah_oman_weather_aod_pm2023-2025.csv`
  - `Musandam_oman_weather_aod_pm2023-2025.csv`
- **Purpose**: Historical weather and air quality data
- **Usage**: Enhanced training data for better ML model accuracy

### 🛠️ Setup and Documentation

#### `README.md` (Main Documentation)
- **Purpose**: Comprehensive project documentation
- **Sections**:
  - Project overview and features
  - Installation instructions
  - API setup guide
  - Usage instructions
  - Technical architecture
  - Troubleshooting
- **Importance**: Critical for users to understand and run the project

#### `requirements.txt` (Python Dependencies)
- **Purpose**: Lists all required Python packages
- **Content**:
  ```
  numpy>=1.21.0
  pandas>=1.3.0
  scikit-learn>=1.0.0
  xgboost>=1.5.0
  joblib>=1.1.0
  ```
- **Usage**: `pip install -r requirements.txt`

#### `install_requirements.py` (Automated Setup)
- **Purpose**: One-click Python dependency installation
- **Features**:
  - Automatic pip installation
  - Error handling and user feedback
  - Cross-platform compatibility
- **Usage**: `python install_requirements.py`

#### `.gitignore` (File Exclusions)
- **Purpose**: Excludes unnecessary files from repository
- **Excludes**:
  - Large model files (*.pkl, *.joblib)
  - Python cache (__pycache__)
  - R session data (.RData, .Rhistory)
  - System files (.DS_Store, Thumbs.db)
- **Benefits**: Keeps repository clean and lightweight

### 🚫 Files NOT to Upload

#### Large Model Files (Excluded by .gitignore)
- `air_quality_flight_safety_models.pkl` (~50-100MB)
- `*.joblib` files (model backups)
- **Reason**: Too large for GitHub, users generate locally instead

#### System/Cache Files
- `__pycache__/` folder
- `.RData`, `.Rhistory` files
- Temporary processing files
- **Reason**: Not needed for project functionality

## Repository Structure After Upload

```
aviation-safety-dashboard/
├── README.md                           # Main documentation
├── UPLOAD_GUIDE.md                     # This guide
├── enhanced_aviation_dashboard.R        # Main R Shiny app
├── enhanced_aviation_ml.py             # ML model training
├── simple_ml_predictor.py              # ML prediction interface
├── requirements.txt                    # Python dependencies
├── install_requirements.py             # Automated setup
├── .gitignore                          # File exclusions
├── sample.csv                          # Sample training data
├── data/                               # Historical data folder
│   ├── Muscat_oman_weather_aod_pm2023-2025.csv
│   ├── Salalah_oman_weather_aod_pm2023-2025.csv
│   └── Musandam_oman_weather_aod_pm2023-2025.csv
├── datacollection.py                  # Data processing scripts
├── dataset.py                          # Dataset utilities
├── ML&Datacleaning.py                  # Data preprocessing
├── netcdf4_TO_CSV.py                   # NetCDF conversion
└── merra2_data/                        # NASA data folder (optional)
```

## What Users Will Do After Download

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/aviation-safety-dashboard.git
cd aviation-safety-dashboard
```

### 2. Install R Dependencies
```r
install.packages(c("shiny", "shinydashboard", "DT", "plotly", 
                   "leaflet", "reticulate", "httr", "jsonlite", "lubridate"))
```

### 3. Install Python Dependencies
```bash
python install_requirements.py
```

### 4. Train ML Models
```bash
python enhanced_aviation_ml.py
```

### 5. Get API Key
- Sign up at [OpenWeatherMap](https://openweathermap.org/api)
- Replace API key in `enhanced_aviation_dashboard.R` (line ~15)

### 6. Run Dashboard
```r
source("enhanced_aviation_dashboard.R")
```

## Repository Description for GitHub

**Title**: `aviation-safety-dashboard`

**Description**: 
```
Real-time Aviation Safety Dashboard for Oman Airports (Muscat, Salalah, Musandam) 
with Weather API Integration, ML-powered Air Quality Predictions, and 48-hour 
Flight Safety Forecasting. Built with R Shiny and Python ML models.
```

**Topics/Tags**:
- `aviation-safety`
- `weather-forecasting`
- `machine-learning`
- `r-shiny`
- `air-quality`
- `flight-safety`
- `real-time-data`
- `oman-airports`

## Key Features to Highlight

✅ **Real-time Weather Integration** - Live data from OpenWeatherMap API  
✅ **Machine Learning Predictions** - AI-powered air quality forecasting  
✅ **48-hour Forecasting** - Sequential weather and safety predictions  
✅ **Interactive Dashboard** - User-friendly web interface  
✅ **Multi-airport Support** - Muscat, Salalah, Musandam coverage  
✅ **Automated Setup** - One-click installation scripts  
✅ **Comprehensive Documentation** - Complete setup and usage guide  

Your repository will be professional, well-documented, and ready for collaboration! 🚀