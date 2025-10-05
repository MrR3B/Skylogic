import pandas as pd
import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Set up plotting style
plt.style.use('default')
sns.set_palette("husl")

# Load and prepare data (same as before)
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

# Add temporal features
df['Hour'] = df['DateTime'].dt.hour
df['DayOfWeek'] = df['DateTime'].dt.dayofweek
df['Month'] = df['DateTime'].dt.month
df['Season'] = df['Month'].map({12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3})

if "Heat Index (°C)" in df.columns:
    df = df.drop(columns=["Heat Index (°C)"])

df = df.dropna()

# Prepare features
features = ["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)",
            "Wind Direction (°)", "Pressure (hPa)", "Dust (µg/m³)", 
            "Aerosol Optical Depth", "Hour", "DayOfWeek", "Month", "Season"]

city_dummies = pd.get_dummies(df['City'], prefix='City')
feature_df = pd.concat([df[features], city_dummies], axis=1)

X = feature_df
y_pm25 = df["PM2.5 (µg/m³)"]
y_pm10 = df["PM10 (µg/m³)"]

# Train optimized model
X_train, X_test, y_train_pm25, y_test_pm25 = train_test_split(X, y_pm25, test_size=0.3, random_state=42)
_, _, y_train_pm10, y_test_pm10 = train_test_split(X, y_pm10, test_size=0.3, random_state=42)

# Best model from grid search
best_model_pm25 = RandomForestRegressor(n_estimators=300, max_depth=None, 
                                       min_samples_leaf=1, min_samples_split=2, 
                                       random_state=42)
best_model_pm25.fit(X_train, y_train_pm25)
y_pred_pm25 = best_model_pm25.predict(X_test)

# Train PM10 model
best_model_pm10 = RandomForestRegressor(n_estimators=300, max_depth=None, 
                                       min_samples_leaf=1, min_samples_split=2, 
                                       random_state=42)
best_model_pm10.fit(X_train, y_train_pm10)
y_pred_pm10 = best_model_pm10.predict(X_test)

# Create comprehensive visualizations
fig = plt.figure(figsize=(20, 15))

# 1. Actual vs Predicted scatter plot for PM2.5
plt.subplot(3, 4, 1)
plt.scatter(y_test_pm25, y_pred_pm25, alpha=0.5, s=1)
plt.plot([y_test_pm25.min(), y_test_pm25.max()], [y_test_pm25.min(), y_test_pm25.max()], 'r--', lw=2)
plt.xlabel('Actual PM2.5 (µg/m³)')
plt.ylabel('Predicted PM2.5 (µg/m³)')
plt.title(f'PM2.5: Actual vs Predicted\nR² = {r2_score(y_test_pm25, y_pred_pm25):.3f}')

# 2. Actual vs Predicted scatter plot for PM10
plt.subplot(3, 4, 2)
plt.scatter(y_test_pm10, y_pred_pm10, alpha=0.5, s=1)
plt.plot([y_test_pm10.min(), y_test_pm10.max()], [y_test_pm10.min(), y_test_pm10.max()], 'r--', lw=2)
plt.xlabel('Actual PM10 (µg/m³)')
plt.ylabel('Predicted PM10 (µg/m³)')
plt.title(f'PM10: Actual vs Predicted\nR² = {r2_score(y_test_pm10, y_pred_pm10):.3f}')

# 3. Residual plot for PM2.5
plt.subplot(3, 4, 3)
residuals_pm25 = y_test_pm25 - y_pred_pm25
plt.scatter(y_pred_pm25, residuals_pm25, alpha=0.5, s=1)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted PM2.5 (µg/m³)')
plt.ylabel('Residuals')
plt.title('PM2.5 Residual Plot')

# 4. Residual plot for PM10
plt.subplot(3, 4, 4)
residuals_pm10 = y_test_pm10 - y_pred_pm10
plt.scatter(y_pred_pm10, residuals_pm10, alpha=0.5, s=1)
plt.axhline(y=0, color='r', linestyle='--')
plt.xlabel('Predicted PM10 (µg/m³)')
plt.ylabel('Residuals')
plt.title('PM10 Residual Plot')

# 5. Feature importance for PM2.5
plt.subplot(3, 4, 5)
feature_importance_pm25 = pd.DataFrame({
    'feature': X_train.columns,
    'importance': best_model_pm25.feature_importances_
}).sort_values('importance', ascending=True).tail(10)

plt.barh(range(len(feature_importance_pm25)), feature_importance_pm25['importance'])
plt.yticks(range(len(feature_importance_pm25)), feature_importance_pm25['feature'])
plt.xlabel('Importance')
plt.title('Top 10 Features - PM2.5')

# 6. Feature importance for PM10
plt.subplot(3, 4, 6)
feature_importance_pm10 = pd.DataFrame({
    'feature': X_train.columns,
    'importance': best_model_pm10.feature_importances_
}).sort_values('importance', ascending=True).tail(10)

plt.barh(range(len(feature_importance_pm10)), feature_importance_pm10['importance'])
plt.yticks(range(len(feature_importance_pm10)), feature_importance_pm10['feature'])
plt.xlabel('Importance')
plt.title('Top 10 Features - PM10')

# 7. Distribution comparison for PM2.5
plt.subplot(3, 4, 7)
plt.hist(y_test_pm25, bins=50, alpha=0.5, label='Actual', density=True)
plt.hist(y_pred_pm25, bins=50, alpha=0.5, label='Predicted', density=True)
plt.xlabel('PM2.5 (µg/m³)')
plt.ylabel('Density')
plt.title('PM2.5 Distribution Comparison')
plt.legend()

# 8. Distribution comparison for PM10
plt.subplot(3, 4, 8)
plt.hist(y_test_pm10, bins=50, alpha=0.5, label='Actual', density=True)
plt.hist(y_pred_pm10, bins=50, alpha=0.5, label='Predicted', density=True)
plt.xlabel('PM10 (µg/m³)')
plt.ylabel('Density')
plt.title('PM10 Distribution Comparison')
plt.legend()

# 9. PM2.5 by City
plt.subplot(3, 4, 9)
city_data = []
for city in df['City'].unique():
    city_mask = df['City'] == city
    city_data.append(df[city_mask]['PM2.5 (µg/m³)'])
plt.boxplot(city_data, labels=df['City'].unique())
plt.ylabel('PM2.5 (µg/m³)')
plt.title('PM2.5 Distribution by City')
plt.xticks(rotation=45)

# 10. PM10 by City
plt.subplot(3, 4, 10)
city_data_pm10 = []
for city in df['City'].unique():
    city_mask = df['City'] == city
    city_data_pm10.append(df[city_mask]['PM10 (µg/m³)'])
plt.boxplot(city_data_pm10, labels=df['City'].unique())
plt.ylabel('PM10 (µg/m³)')
plt.title('PM10 Distribution by City')
plt.xticks(rotation=45)

# 11. Temporal pattern - PM2.5 by hour
plt.subplot(3, 4, 11)
hourly_pm25 = df.groupby('Hour')['PM2.5 (µg/m³)'].mean()
plt.plot(hourly_pm25.index, hourly_pm25.values, marker='o')
plt.xlabel('Hour of Day')
plt.ylabel('Mean PM2.5 (µg/m³)')
plt.title('Daily PM2.5 Pattern')
plt.xticks(range(0, 24, 4))

# 12. Seasonal pattern - PM2.5 by month
plt.subplot(3, 4, 12)
monthly_pm25 = df.groupby('Month')['PM2.5 (µg/m³)'].mean()
plt.plot(monthly_pm25.index, monthly_pm25.values, marker='o')
plt.xlabel('Month')
plt.ylabel('Mean PM2.5 (µg/m³)')
plt.title('Seasonal PM2.5 Pattern')
plt.xticks(range(1, 13))

plt.tight_layout()
plt.savefig('ml_model_analysis.png', dpi=300, bbox_inches='tight')
print("Visualization saved as 'ml_model_analysis.png'")

# Print comprehensive model evaluation
print("\n" + "="*60)
print("COMPREHENSIVE MODEL EVALUATION REPORT")
print("="*60)

print(f"\nDataset Overview:")
print(f"- Total records: {len(df):,}")
print(f"- Time period: {df['DateTime'].min().date()} to {df['DateTime'].max().date()}")
print(f"- Cities: {', '.join(df['City'].unique())}")

print(f"\nPM2.5 Model Performance:")
mae_pm25 = mean_absolute_error(y_test_pm25, y_pred_pm25)
rmse_pm25 = np.sqrt(mean_squared_error(y_test_pm25, y_pred_pm25))
r2_pm25 = r2_score(y_test_pm25, y_pred_pm25)
print(f"- MAE: {mae_pm25:.2f} µg/m³")
print(f"- RMSE: {rmse_pm25:.2f} µg/m³")
print(f"- R²: {r2_pm25:.3f}")
print(f"- Error percentage: {(mae_pm25/y_test_pm25.mean()*100):.1f}%")

print(f"\nPM10 Model Performance:")
mae_pm10 = mean_absolute_error(y_test_pm10, y_pred_pm10)
rmse_pm10 = np.sqrt(mean_squared_error(y_test_pm10, y_pred_pm10))
r2_pm10 = r2_score(y_test_pm10, y_pred_pm10)
print(f"- MAE: {mae_pm10:.2f} µg/m³")
print(f"- RMSE: {rmse_pm10:.2f} µg/m³")
print(f"- R²: {r2_pm10:.3f}")
print(f"- Error percentage: {(mae_pm10/y_test_pm10.mean()*100):.1f}%")

print(f"\nKey Insights:")
print(f"- Dust concentration is the most important predictor for PM2.5 ({feature_importance_pm25.iloc[-1]['importance']:.1%})")
print(f"- PM2.5 varies significantly by city: Muscat ({df[df['City']=='Muscat']['PM2.5 (µg/m³)'].mean():.1f}) > Musandam ({df[df['City']=='Musandam']['PM2.5 (µg/m³)'].mean():.1f}) > Salalah ({df[df['City']=='Salalah']['PM2.5 (µg/m³)'].mean():.1f})")
print(f"- PM10 shows extreme values in Salalah (max: {df[df['City']=='Salalah']['PM10 (µg/m³)'].max():.1f} µg/m³)")

plt.show()