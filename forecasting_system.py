import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class AirQualityForecaster:
    """
    48-hour air quality forecasting system for proactive decision making
    Uses time series features and weather patterns to predict future conditions
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        
    def create_time_series_features(self, df):
        """Create lagged features for time series forecasting"""
        df = df.sort_values('DateTime').reset_index(drop=True)
        
        # Create lag features (previous hours)
        lag_hours = [1, 2, 3, 6, 12, 24]
        lag_columns = ['PM2.5 (µg/m³)', 'PM10 (µg/m³)', 'Temperature (°C)', 
                      'Humidity (%)', 'Wind Speed (m/s)', 'Dust (µg/m³)']
        
        for col in lag_columns:
            for lag in lag_hours:
                df[f'{col}_lag_{lag}h'] = df[col].shift(lag)
        
        # Rolling statistics (moving averages)
        for col in lag_columns:
            df[f'{col}_rolling_6h'] = df[col].rolling(window=6, min_periods=1).mean()
            df[f'{col}_rolling_24h'] = df[col].rolling(window=24, min_periods=1).mean()
        
        # Seasonal components
        df['hour_sin'] = np.sin(2 * np.pi * df['DateTime'].dt.hour / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['DateTime'].dt.hour / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['DateTime'].dt.dayofyear / 365)
        df['day_cos'] = np.cos(2 * np.pi * df['DateTime'].dt.dayofyear / 365)
        
        return df
    
    def prepare_forecast_data(self):
        """Load and prepare data for forecasting"""
        print("Preparing data for 48-hour forecasting...")
        
        # Load historical data
        files = ['./data/Muscat_oman_weather_aod_pm2023-2025.csv',
                './data/Musandam_oman_weather_aod_pm2023-2025.csv', 
                './data/Salalah_oman_weather_aod_pm2023-2025.csv']
        
        df_list = []
        for f in files:
            try:
                temp_df = pd.read_csv(f)
                city_name = f.split('/')[-1].split('_')[0].replace('./data\\', '')
                temp_df['City'] = city_name
                df_list.append(temp_df)
            except:
                continue
        
        if not df_list:
            raise ValueError("No data files found!")
            
        df = pd.concat(df_list, ignore_index=True)
        df.columns = [c.replace("Â", "").strip() for c in df.columns]
        df["DateTime"] = pd.to_datetime(df["DateTime"])
        
        # Sort by city and time
        df = df.sort_values(['City', 'DateTime']).reset_index(drop=True)
        
        # Create time series features
        city_dfs = []
        for city in df['City'].unique():
            city_df = df[df['City'] == city].copy()
            city_df = self.create_time_series_features(city_df)
            city_dfs.append(city_df)
        
        df = pd.concat(city_dfs, ignore_index=True)
        
        # Remove rows with NaN values (due to lag features)
        df = df.dropna()
        
        print(f"Prepared {len(df)} records for forecasting")
        return df
    
    def train_forecast_models(self):
        """Train models for 1, 6, 12, 24, and 48 hour forecasts"""
        df = self.prepare_forecast_data()
        
        # Define forecast horizons
        horizons = [1, 6, 12, 24, 48]  # hours ahead
        
        # Feature columns (excluding target variables and datetime)
        exclude_cols = ['DateTime', 'City', 'PM2.5 (µg/m³)', 'PM10 (µg/m³)']
        if 'Heat Index (°C)' in df.columns:
            exclude_cols.append('Heat Index (°C)')
            
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Add city dummies
        city_dummies = pd.get_dummies(df['City'], prefix='City')
        X = pd.concat([df[feature_cols], city_dummies], axis=1)
        
        self.feature_columns = X.columns.tolist()
        
        print(f"Training forecast models with {len(self.feature_columns)} features...")
        
        for horizon in horizons:
            print(f"\nTraining {horizon}-hour forecast models...")
            
            # Create future targets by shifting backwards
            y_pm25 = df['PM2.5 (µg/m³)'].shift(-horizon).dropna()
            y_pm10 = df['PM10 (µg/m³)'].shift(-horizon).dropna()
            
            # Align X with y
            X_aligned = X.iloc[:len(y_pm25)]
            
            if len(X_aligned) < 100:  # Not enough data
                print(f"  Insufficient data for {horizon}-hour forecast")
                continue
            
            # Train PM2.5 model
            model_pm25 = RandomForestRegressor(
                n_estimators=200, 
                max_depth=15,
                min_samples_split=5,
                random_state=42
            )
            model_pm25.fit(X_aligned, y_pm25)
            
            # Train PM10 model  
            model_pm10 = RandomForestRegressor(
                n_estimators=200,
                max_depth=15, 
                min_samples_split=5,
                random_state=42
            )
            model_pm10.fit(X_aligned, y_pm10)
            
            # Store models
            self.models[f'pm25_{horizon}h'] = model_pm25
            self.models[f'pm10_{horizon}h'] = model_pm10
            
            print(f"  ✅ {horizon}-hour models trained")
        
        print(f"\n✅ All forecast models trained successfully!")
    
    def forecast_next_48_hours(self, current_conditions):
        """
        Generate 48-hour forecast using current conditions
        
        Args:
            current_conditions: DataFrame with latest data point
        """
        forecasts = {}
        horizons = [1, 6, 12, 24, 48]
        
        # Prepare current conditions
        if 'City' in current_conditions.columns:
            city_dummies = pd.get_dummies(current_conditions['City'], prefix='City')
            # Ensure all city columns are present
            for col in self.feature_columns:
                if col.startswith('City_') and col not in city_dummies.columns:
                    city_dummies[col] = 0
        else:
            # Default to Muscat if no city specified
            city_dummies = pd.DataFrame({col: [1 if col == 'City_Muscat' else 0] 
                                       for col in self.feature_columns if col.startswith('City_')})
        
        # Create feature vector
        base_features = [col for col in self.feature_columns if not col.startswith('City_')]
        X_current = pd.concat([current_conditions[base_features], city_dummies], axis=1)
        
        # Ensure all feature columns are present
        for col in self.feature_columns:
            if col not in X_current.columns:
                X_current[col] = 0
        
        # Reorder columns to match training
        X_current = X_current[self.feature_columns]
        
        for horizon in horizons:
            if f'pm25_{horizon}h' in self.models and f'pm10_{horizon}h' in self.models:
                pm25_pred = self.models[f'pm25_{horizon}h'].predict(X_current)[0]
                pm10_pred = self.models[f'pm10_{horizon}h'].predict(X_current)[0]
                
                forecasts[f'{horizon}h'] = {
                    'pm25': max(0, pm25_pred),  # Ensure non-negative
                    'pm10': max(0, pm10_pred),
                    'timestamp': datetime.now() + timedelta(hours=horizon)
                }
        
        return forecasts
    
    def generate_forecast_alerts(self, forecasts):
        """Generate alerts based on forecast predictions"""
        alerts = []
        
        for horizon, pred in forecasts.items():
            pm25 = pred['pm25']
            pm10 = pred['pm10']
            timestamp = pred['timestamp']
            
            # Calculate AQI
            aqi_pm25 = self.calculate_aqi(pm25, 'pm25')
            aqi_pm10 = self.calculate_aqi(pm10, 'pm10')
            overall_aqi = max(aqi_pm25, aqi_pm10)
            
            if overall_aqi > 150:  # Unhealthy
                alerts.append({
                    'horizon': horizon,
                    'level': 'HIGH',
                    'message': f"Unhealthy air quality predicted in {horizon} (AQI: {overall_aqi:.0f})",
                    'timestamp': timestamp,
                    'aqi': overall_aqi
                })
            elif overall_aqi > 100:  # Moderate
                alerts.append({
                    'horizon': horizon,
                    'level': 'MODERATE', 
                    'message': f"Moderate air quality predicted in {horizon} (AQI: {overall_aqi:.0f})",
                    'timestamp': timestamp,
                    'aqi': overall_aqi
                })
        
        return alerts
    
    def calculate_aqi(self, concentration, pollutant):
        """Calculate AQI for a single concentration value"""
        if pollutant == 'pm25':
            breakpoints = [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                          (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400)]
        else:  # pm10
            breakpoints = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                          (255, 354, 151, 200), (355, 424, 201, 300), (425, 504, 301, 400)]
        
        for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
            if bp_low <= concentration <= bp_high:
                aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (concentration - bp_low) + aqi_low
                return aqi
        
        return 500  # Above highest breakpoint
    
    def save_forecast_models(self):
        """Save trained forecast models"""
        forecast_data = {
            'models': self.models,
            'feature_columns': self.feature_columns
        }
        joblib.dump(forecast_data, 'air_quality_forecast_models.pkl')
        print("✅ Forecast models saved to 'air_quality_forecast_models.pkl'")

def main():
    """Main forecasting system demonstration"""
    print("=== 48-HOUR AIR QUALITY FORECASTING SYSTEM ===")
    print("Proactive predictions for safer skies and cleaner air")
    print("="*60)
    
    # Initialize forecaster
    forecaster = AirQualityForecaster()
    
    # Train models
    try:
        forecaster.train_forecast_models()
        forecaster.save_forecast_models()
        
        # Demo forecast with sample current conditions
        print("\n" + "="*60)
        print("SAMPLE 48-HOUR FORECAST")
        print("="*60)
        
        # Sample current conditions (latest values from your data)
        current_conditions = pd.DataFrame({
            'Temperature (°C)': [30.5],
            'Humidity (%)': [45.0],
            'Wind Speed (m/s)': [12.0],
            'Wind Direction (°)': [180.0],
            'Pressure (hPa)': [1015.0],
            'Dust (µg/m³)': [95.0],
            'Aerosol Optical Depth': [0.25],
            'City': ['Muscat'],
            # Add lag features (simplified - in real system, these would be from recent history)
            'PM2.5 (µg/m³)_lag_1h': [25.0],
            'PM2.5 (µg/m³)_lag_24h': [22.0],
            'PM10 (µg/m³)_lag_1h': [65.0],
            'PM10 (µg/m³)_lag_24h': [58.0],
            'Temperature (°C)_lag_1h': [29.8],
            'Humidity (%)_lag_1h': [47.0],
            'Wind Speed (m/s)_lag_1h': [11.5],
            'Dust (µg/m³)_lag_1h': [88.0],
            'PM2.5 (µg/m³)_rolling_6h': [24.0],
            'PM2.5 (µg/m³)_rolling_24h': [23.5],
            'PM10 (µg/m³)_rolling_6h': [62.0],
            'PM10 (µg/m³)_rolling_24h': [60.0],
            'hour_sin': [np.sin(2 * np.pi * 12 / 24)],
            'hour_cos': [np.cos(2 * np.pi * 12 / 24)],
            'day_sin': [np.sin(2 * np.pi * 276 / 365)],  # Day 276 of year
            'day_cos': [np.cos(2 * np.pi * 276 / 365)]
        })
        
        # Add missing lag features with default values
        required_features = [col for col in forecaster.feature_columns if not col.startswith('City_')]
        for feature in required_features:
            if feature not in current_conditions.columns:
                current_conditions[feature] = 0.0  # Default value
        
        # Generate forecast
        forecasts = forecaster.forecast_next_48_hours(current_conditions)
        alerts = forecaster.generate_forecast_alerts(forecasts)
        
        print("\n📊 48-Hour Air Quality Forecast:")
        print("-" * 50)
        for horizon, pred in forecasts.items():
            print(f"{horizon:>4}: PM2.5={pred['pm25']:5.1f} µg/m³, PM10={pred['pm10']:5.1f} µg/m³ "
                  f"({pred['timestamp'].strftime('%Y-%m-%d %H:%M')})")
        
        if alerts:
            print(f"\n🚨 FORECAST ALERTS:")
            for alert in alerts:
                print(f"  [{alert['level']}] {alert['message']}")
        else:
            print(f"\n✅ No air quality alerts in the next 48 hours")
        
        print(f"\n🎯 Forecasting system ready for deployment!")
        print("   - 48-hour predictions available")
        print("   - Proactive alert system configured") 
        print("   - Ready for integration with dashboard")
        
    except Exception as e:
        print(f"❌ Error in forecasting system: {str(e)}")
        print("This may be due to insufficient historical data for time series features.")
        print("The system needs several weeks of continuous data to train properly.")

if __name__ == "__main__":
    main()