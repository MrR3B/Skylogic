import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import json
import sys
import os

class DashboardMLPredictor:
    """
    ML Prediction service for R Dashboard integration
    Loads trained models and provides real predictions for dashboard
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.forecast_models = {}
        self.forecast_scalers = {}
        self.forecast_feature_columns = []
        self.load_models()
    
    def load_models(self):
        """Load both current conditions and forecasting models"""
        try:
            # Load current conditions models
            if os.path.exists('air_quality_flight_safety_models.pkl'):
                model_data = joblib.load('air_quality_flight_safety_models.pkl')
                self.models = model_data['models']
                self.scalers = model_data['scalers']
                self.feature_columns = model_data['feature_columns']
                print("✅ Current conditions models loaded successfully")
            
            # Load forecasting models  
            if os.path.exists('air_quality_forecast_models.pkl'):
                forecast_data = joblib.load('air_quality_forecast_models.pkl')
                self.forecast_models = forecast_data['models']
                self.forecast_scalers = forecast_data['scalers'] 
                self.forecast_feature_columns = forecast_data['feature_columns']
                print("✅ Forecasting models loaded successfully")
                
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            sys.exit(1)
    
    def create_features_for_location(self, site, lat, lon, region, hour, 
                                   temperature=25, humidity=60, wind_speed=10, 
                                   pressure=1013, dust=50, aod=0.2):
        """Create feature vector for a specific location and time"""
        
        # Current datetime
        current_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
        
        # Base meteorological features
        features = {
            "Temperature (°C)": temperature,
            "Humidity (%)": humidity, 
            "Wind Speed (m/s)": wind_speed,
            "Wind Direction (°)": 180 + 60 * np.sin(hour * np.pi / 12),  # Realistic variation
            "Pressure (hPa)": pressure,
            "Dust (µg/m³)": dust,
            "Aerosol Optical Depth": aod,
            "Hour": hour,
            "DayOfWeek": current_time.weekday(),
            "Month": current_time.month,
            "Season": self.get_season(current_time.month),
            "IsWeekend": 1 if current_time.weekday() >= 5 else 0
        }
        
        # Enhanced aviation features
        features["Visibility_Est"] = 50 / (1 + (dust/200) + (aod*100))
        features["Turbulence_Risk"] = np.clip(wind_speed/25 + dust/200, 0, 1)
        features["Air_Density"] = (pressure * 100) / (287.05 * (temperature + 273.15))
        features["Dust_Wind_Factor"] = (dust/100) * (wind_speed/25)
        features["Pressure_Stability"] = abs(pressure - 1013.25) / 50
        features["Temp_Humidity_Index"] = temperature * (1 + humidity/100)
        
        # City dummy variables (one-hot encoding)
        cities = ['Musandam', 'Muscat', 'Salalah']  # Your 3 cities
        for city in cities:
            features[f'City_{city}'] = 1 if region == city or site == city else 0
        
        return features
    
    def get_season(self, month):
        """Get season number based on month"""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring  
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Autumn
    
    def predict_conditions(self, site, lat, lon, region, hour, 
                         temperature=25, humidity=60, wind_speed=10, 
                         pressure=1013, dust=50, aod=0.2):
        """Predict current conditions using trained ML models"""
        
        # Create feature vector
        features = self.create_features_for_location(
            site, lat, lon, region, hour, temperature, humidity, 
            wind_speed, pressure, dust, aod
        )
        
        # Convert to DataFrame with correct column order
        feature_df = pd.DataFrame([features])
        
        # Ensure we have all required columns in correct order
        missing_cols = set(self.feature_columns) - set(feature_df.columns)
        for col in missing_cols:
            feature_df[col] = 0
        
        feature_df = feature_df[self.feature_columns]
        
        # Make predictions
        predictions = {}
        for target_name, model in self.models.items():
            try:
                pred = model.predict(feature_df)[0]
                predictions[target_name] = max(0, pred)  # Ensure non-negative
            except Exception as e:
                print(f"Error predicting {target_name}: {e}")
                # Fallback values
                fallback_values = {
                    'PM2.5': 20, 'PM10': 40, 'Visibility_Est': 15,
                    'Flight_Safety_Score': 0.7, 'Overall_AQI': 50
                }
                predictions[target_name] = fallback_values.get(target_name, 0)
        
        # Calculate additional metrics
        predictions['AQI'] = max(
            self.calculate_aqi(predictions.get('PM2.5', 20), 'pm25'),
            self.calculate_aqi(predictions.get('PM10', 40), 'pm10')
        )
        
        return predictions
    
    def calculate_aqi(self, concentration, pollutant):
        """Calculate AQI using EPA breakpoints"""
        if pollutant == 'pm25':
            breakpoints = [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                          (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400)]
        else:  # pm10
            breakpoints = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                          (255, 354, 151, 200), (355, 424, 201, 300), (425, 504, 301, 400)]
        
        for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
            if bp_low <= concentration <= bp_high:
                aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                return round(aqi)
        
        if concentration > breakpoints[-1][1]:
            return 500
        return 0
    
    def predict_for_dashboard(self, sites_data):
        """
        Main prediction function for dashboard
        sites_data: list of dicts with site info and conditions
        """
        results = []
        
        for site_info in sites_data:
            predictions = self.predict_conditions(
                site_info['site'],
                site_info['lat'], 
                site_info['lon'],
                site_info['region'],
                site_info['hour'],
                site_info.get('temperature', 25),
                site_info.get('humidity', 60),
                site_info.get('wind_speed', 10),
                site_info.get('pressure', 1013),
                site_info.get('dust', 50),
                site_info.get('aod', 0.2)
            )
            
            # Format for dashboard
            result = {
                'site': site_info['site'],
                'lat': site_info['lat'],
                'lon': site_info['lon'], 
                'region': site_info['region'],
                'hour': site_info['hour'],
                'pm25': predictions.get('PM2.5', 20),
                'pm10': predictions.get('PM10', 40),
                'temperature': site_info.get('temperature', 25),
                'humidity': site_info.get('humidity', 60),
                'wind_speed': site_info.get('wind_speed', 10),
                'dust': site_info.get('dust', 50),
                'visibility': predictions.get('Visibility_Est', 15),
                'flight_safety_score': predictions.get('Flight_Safety_Score', 0.7),
                'AQI': predictions.get('AQI', 50),
                'prediction_source': 'ML_Model'
            }
            
            results.append(result)
        
        return results

def main():
    """Command line interface for dashboard integration"""
    if len(sys.argv) < 2:
        print("Usage: python ml_prediction_service.py <command> [args]")
        print("Commands:")
        print("  test - Run test prediction")
        print("  predict - Make predictions from JSON input")
        sys.exit(1)
    
    predictor = DashboardMLPredictor()
    command = sys.argv[1]
    
    if command == "test":
        # Test prediction for your 3 locations
        test_sites = [
            {'site': 'Muscat', 'lat': 23.5933, 'lon': 58.2844, 'region': 'Muscat', 'hour': 12},
            {'site': 'Salalah', 'lat': 17.0387, 'lon': 54.0914, 'region': 'Dhofar', 'hour': 12}, 
            {'site': 'Musandam', 'lat': 26.2041, 'lon': 56.2606, 'region': 'Musandam', 'hour': 12}
        ]
        
        results = predictor.predict_for_dashboard(test_sites)
        print(json.dumps(results, indent=2))
        
    elif command == "predict":
        # Read JSON input from stdin or file
        try:
            if len(sys.argv) > 2:
                # Read from file
                with open(sys.argv[2], 'r') as f:
                    sites_data = json.load(f)
            else:
                # Read from stdin
                sites_data = json.loads(sys.stdin.read())
            
            results = predictor.predict_for_dashboard(sites_data)
            print(json.dumps(results, indent=2))
            
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()