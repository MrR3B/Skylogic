import pandas as pd
import glob
import numpy as np
from sklearn.model_selection import train_test_split, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor, VotingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=== ENHANCED AIR QUALITY & AVIATION SAFETY PREDICTION SYSTEM ===")
print("Real-time predictions for safer skies and cleaner air")
print("="*70)

class AirQualityFlightSafetyPredictor:
    def __init__(self):
        """Initialize the enhanced prediction system"""
        self.models = {}
        self.scalers = {}
        self.feature_columns = []
        self.thresholds = {
            'pm25': {'good': 12, 'moderate': 35.4, 'unhealthy_sensitive': 55.4, 'unhealthy': 150.4, 'very_unhealthy': 250.4},
            'pm10': {'good': 54, 'moderate': 154, 'unhealthy_sensitive': 254, 'unhealthy': 354, 'very_unhealthy': 424},
            'visibility': {'poor': 5, 'reduced': 10, 'good': 25},  # km
            'flight_safety': {'high_risk': 0.3, 'moderate_risk': 0.6, 'low_risk': 1.0}
        }
    
    def load_and_prepare_data(self):
        """Enhanced data loading with aviation-specific features"""
        print("Loading and preparing enhanced dataset...")
        
        # Load data from all cities
        files = glob.glob("./data/*.csv")
        df_list = []
        
        for f in files:
            temp_df = pd.read_csv(f)
            city_name = f.split('/')[-1].split('_')[0].replace('data\\', '')
            temp_df['City'] = city_name
            df_list.append(temp_df)
        
        df = pd.concat(df_list, ignore_index=True)
        df.columns = [c.replace("Â", "").strip() for c in df.columns]
        df["DateTime"] = pd.to_datetime(df["DateTime"])
        
        if "Heat Index (°C)" in df.columns:
            df = df.drop(columns=["Heat Index (°C)"])
        
        # Enhanced feature engineering for aviation safety
        print("Creating aviation-specific features...")
        
        # Temporal features
        df['Hour'] = df['DateTime'].dt.hour
        df['DayOfWeek'] = df['DateTime'].dt.dayofweek
        df['Month'] = df['DateTime'].dt.month
        df['Season'] = df['Month'].map({12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3})
        df['IsWeekend'] = (df['DayOfWeek'] >= 5).astype(int)
        
        # Aviation-specific calculations
        df['Visibility_Est'] = self.calculate_visibility(df['PM2.5 (µg/m³)'], df['PM10 (µg/m³)'], df['Dust (µg/m³)'])
        df['Turbulence_Risk'] = self.calculate_turbulence_risk(df['Wind Speed (m/s)'], df['Dust (µg/m³)'], df['Temperature (°C)'])
        df['Air_Density'] = self.calculate_air_density(df['Temperature (°C)'], df['Pressure (hPa)'], df['Humidity (%)'])
        df['Dust_Wind_Factor'] = df['Dust (µg/m³)'] * df['Wind Speed (m/s)'] / 100
        df['Pollution_Index'] = (df['PM2.5 (µg/m³)'] * 2 + df['PM10 (µg/m³)']) / 3
        
        # Weather stability indicators
        df['Pressure_Stability'] = abs(df['Pressure (hPa)'] - df['Pressure (hPa)'].rolling(24).mean())
        df['Temp_Humidity_Index'] = df['Temperature (°C)'] * (df['Humidity (%)'] / 100)
        
        # Risk categorization
        df['AQI_PM25'] = self.calculate_aqi(df['PM2.5 (µg/m³)'], 'pm25')
        df['AQI_PM10'] = self.calculate_aqi(df['PM10 (µg/m³)'], 'pm10')
        df['Overall_AQI'] = np.maximum(df['AQI_PM25'], df['AQI_PM10'])
        df['Flight_Safety_Score'] = self.calculate_flight_safety_score(df)
        
        # Remove NaN values first
        df = df.dropna()
        
        # City encoding after removing NaN
        city_dummies = pd.get_dummies(df['City'], prefix='City')
        
        self.data = df
        print(f"Data prepared: {len(self.data)} records from {df['DateTime'].min().date()} to {df['DateTime'].max().date()}")
        
        return self.data, city_dummies
    
    def calculate_visibility(self, pm25, pm10, dust):
        """Estimate visibility based on particulate matter (simplified model)"""
        # Simplified visibility estimation (km)
        visibility = 50 / (1 + (pm25/50) + (pm10/100) + (dust/200))
        return np.clip(visibility, 0.1, 50)
    
    def calculate_turbulence_risk(self, wind_speed, dust, temperature):
        """Calculate turbulence risk factor (0-1, higher = more risk)"""
        # Factors that increase turbulence risk
        wind_factor = np.clip(wind_speed / 20, 0, 1)  # High wind speeds
        dust_factor = np.clip(dust / 500, 0, 1)       # Dust storms
        temp_factor = np.clip(temperature / 50, 0, 1)  # High temperatures
        
        return (wind_factor * 0.4 + dust_factor * 0.4 + temp_factor * 0.2)
    
    def calculate_air_density(self, temp_c, pressure_hpa, humidity_pct):
        """Calculate air density (affects aircraft performance)"""
        # Simplified air density calculation
        temp_k = temp_c + 273.15
        rh_factor = 1 - (humidity_pct / 100) * 0.02  # Humidity reduces density slightly
        density = (pressure_hpa * 100) / (287.05 * temp_k) * rh_factor
        return density
    
    def calculate_aqi(self, concentration, pollutant):
        """Calculate AQI using EPA breakpoints"""
        if pollutant == 'pm25':
            breakpoints = [(0, 12.0, 0, 50), (12.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
                          (55.5, 150.4, 151, 200), (150.5, 250.4, 201, 300), (250.5, 350.4, 301, 400)]
        else:  # pm10
            breakpoints = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
                          (255, 354, 151, 200), (355, 424, 201, 300), (425, 504, 301, 400)]
        
        aqi_values = []
        for conc in concentration:
            if pd.isna(conc):
                aqi_values.append(np.nan)
                continue
                
            aqi = 0
            for bp_low, bp_high, aqi_low, aqi_high in breakpoints:
                if bp_low <= conc <= bp_high:
                    aqi = ((aqi_high - aqi_low) / (bp_high - bp_low)) * (conc - bp_low) + aqi_low
                    break
            if conc > breakpoints[-1][1]:  # Above highest breakpoint
                aqi = 500
            aqi_values.append(round(aqi))
        
        return np.array(aqi_values)
    
    def calculate_flight_safety_score(self, df):
        """Calculate overall flight safety score (0-1, higher = safer)"""
        # Normalize factors to 0-1 scale
        visibility_score = np.clip(df['Visibility_Est'] / 25, 0, 1)
        low_turbulence_score = 1 - df['Turbulence_Risk']
        air_quality_score = np.clip((300 - df['Overall_AQI']) / 300, 0, 1)
        wind_score = np.clip((25 - df['Wind Speed (m/s)']) / 25, 0, 1)
        
        # Weighted combination
        safety_score = (visibility_score * 0.3 + 
                       low_turbulence_score * 0.3 + 
                       air_quality_score * 0.25 + 
                       wind_score * 0.15)
        
        return np.clip(safety_score, 0, 1)
    
    def prepare_features(self, df, city_dummies):
        """Prepare feature matrix"""
        base_features = [
            "Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)", "Wind Direction (°)",
            "Pressure (hPa)", "Dust (µg/m³)", "Aerosol Optical Depth",
            "Hour", "DayOfWeek", "Month", "Season", "IsWeekend",
            "Visibility_Est", "Turbulence_Risk", "Air_Density", "Dust_Wind_Factor",
            "Pressure_Stability", "Temp_Humidity_Index"
        ]
        
        # Ensure same index for concatenation
        city_dummies = city_dummies.loc[df.index]
        
        # Combine with city dummies
        feature_df = pd.concat([df[base_features], city_dummies], axis=1)
        self.feature_columns = feature_df.columns.tolist()
        
        return feature_df
    
    def train_models(self, X, y_targets):
        """Train enhanced ensemble models"""
        print("\nTraining enhanced ensemble models...")
        
        # Time series split for proper validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        for target_name, y in y_targets.items():
            print(f"\nTraining model for {target_name}...")
            
            # Train-test split
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, 
                                                              random_state=42, shuffle=False)
            
            # Scale features for some models
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Ensemble model
            ensemble = VotingRegressor([
                ('rf', RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42)),
                ('rf2', RandomForestRegressor(n_estimators=300, max_depth=None, random_state=43)),
                ('rf3', RandomForestRegressor(n_estimators=150, max_depth=15, 
                                            min_samples_split=5, random_state=44))
            ])
            
            ensemble.fit(X_train, y_train)
            y_pred = ensemble.predict(X_test)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            print(f"  MAE: {mae:.3f}")
            print(f"  RMSE: {rmse:.3f}")
            print(f"  R²: {r2:.3f}")
            
            # Store model and scaler
            self.models[target_name] = ensemble
            self.scalers[target_name] = scaler
        
        print("\n✅ All models trained successfully!")
    
    def predict_current_conditions(self, input_data):
        """Make predictions for current conditions"""
        predictions = {}
        
        for target_name, model in self.models.items():
            pred = model.predict(input_data)[0]
            predictions[target_name] = pred
        
        return predictions
    
    def generate_alerts(self, predictions):
        """Generate safety alerts based on predictions"""
        alerts = []
        
        # Air Quality Alerts
        if predictions['PM2.5'] > self.thresholds['pm25']['unhealthy']:
            alerts.append({
                'type': 'AIR_QUALITY',
                'level': 'HIGH',
                'message': f"High PM2.5 levels ({predictions['PM2.5']:.1f} µg/m³). Avoid outdoor activities.",
                'color': 'red'
            })
        elif predictions['PM2.5'] > self.thresholds['pm25']['moderate']:
            alerts.append({
                'type': 'AIR_QUALITY',
                'level': 'MODERATE',
                'message': f"Moderate PM2.5 levels ({predictions['PM2.5']:.1f} µg/m³). Sensitive groups should limit exposure.",
                'color': 'orange'
            })
        
        # Flight Safety Alerts
        if predictions['Flight_Safety_Score'] < self.thresholds['flight_safety']['high_risk']:
            alerts.append({
                'type': 'FLIGHT_SAFETY',
                'level': 'HIGH',
                'message': f"Poor flight conditions (Safety Score: {predictions['Flight_Safety_Score']:.2f}). Consider flight delays.",
                'color': 'red'
            })
        elif predictions['Flight_Safety_Score'] < self.thresholds['flight_safety']['moderate_risk']:
            alerts.append({
                'type': 'FLIGHT_SAFETY',
                'level': 'MODERATE',
                'message': f"Moderate flight conditions (Safety Score: {predictions['Flight_Safety_Score']:.2f}). Monitor conditions closely.",
                'color': 'orange'
            })
        
        # Visibility Alerts
        if predictions['Visibility_Est'] < self.thresholds['visibility']['poor']:
            alerts.append({
                'type': 'VISIBILITY',
                'level': 'HIGH',
                'message': f"Poor visibility ({predictions['Visibility_Est']:.1f} km). Flight operations may be affected.",
                'color': 'red'
            })
        
        return alerts
    
    def save_models(self):
        """Save trained models for deployment"""
        model_data = {
            'models': self.models,
            'scalers': self.scalers,
            'feature_columns': self.feature_columns,
            'thresholds': self.thresholds
        }
        joblib.dump(model_data, 'air_quality_flight_safety_models.pkl')
        print("✅ Models saved to 'air_quality_flight_safety_models.pkl'")

def main():
    # Initialize the prediction system
    predictor = AirQualityFlightSafetyPredictor()
    
    # Load and prepare data
    data, city_dummies = predictor.load_and_prepare_data()
    
    # Prepare features
    X = predictor.prepare_features(data, city_dummies)
    
    # Define target variables
    y_targets = {
        'PM2.5': data['PM2.5 (µg/m³)'],
        'PM10': data['PM10 (µg/m³)'],
        'Visibility_Est': data['Visibility_Est'],
        'Flight_Safety_Score': data['Flight_Safety_Score'],
        'Overall_AQI': data['Overall_AQI']
    }
    
    # Train models
    predictor.train_models(X, y_targets)
    
    # Save models
    predictor.save_models()
    
    # Demonstration with sample prediction
    print("\n" + "="*70)
    print("SAMPLE REAL-TIME PREDICTION")
    print("="*70)
    
    # Use latest data point as example
    sample_input = X.iloc[-1:].values
    predictions = predictor.predict_current_conditions(sample_input)
    
    print(f"\n📍 Current Conditions Prediction:")
    print(f"  PM2.5: {predictions['PM2.5']:.1f} µg/m³")
    print(f"  PM10: {predictions['PM10']:.1f} µg/m³")
    print(f"  Visibility: {predictions['Visibility_Est']:.1f} km")
    print(f"  Flight Safety Score: {predictions['Flight_Safety_Score']:.2f}/1.0")
    print(f"  Overall AQI: {predictions['Overall_AQI']:.0f}")
    
    # Generate alerts
    alerts = predictor.generate_alerts(predictions)
    
    if alerts:
        print(f"\n🚨 ACTIVE ALERTS:")
        for alert in alerts:
            print(f"  [{alert['level']}] {alert['type']}: {alert['message']}")
    else:
        print(f"\n✅ No active alerts - Conditions are within safe ranges")
    
    print("\n🎯 System ready for real-time deployment!")
    print("   - Models trained and validated")
    print("   - Alert system configured")
    print("   - Ready for dashboard integration")

if __name__ == "__main__":
    main()