import pandas as pd
import glob
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

print("=== Enhanced Air Quality ML Analysis ===\n")

# === 1. Load and merge all CSVs ===
files = glob.glob("./data/*.csv")
print(f"Found {len(files)} data files:")
for f in files:
    print(f"  - {f}")

df_list = []
for f in files:
    temp_df = pd.read_csv(f)
    # Add city name from filename
    city_name = f.split('/')[-1].split('_')[0]
    temp_df['City'] = city_name
    df_list.append(temp_df)

df = pd.concat(df_list, ignore_index=True)
print(f"\nTotal records loaded: {len(df)}")

# === 2. Enhanced Data cleaning ===
df.columns = [c.replace("Â", "").strip() for c in df.columns]
df["DateTime"] = pd.to_datetime(df["DateTime"])

# Add temporal features
df['Hour'] = df['DateTime'].dt.hour
df['DayOfWeek'] = df['DateTime'].dt.dayofweek
df['Month'] = df['DateTime'].dt.month
df['Season'] = df['Month'].map({12:0, 1:0, 2:0, 3:1, 4:1, 5:1, 6:2, 7:2, 8:2, 9:3, 10:3, 11:3})

# Remove Heat Index if exists
if "Heat Index (°C)" in df.columns:
    df = df.drop(columns=["Heat Index (°C)"])

print(f"Records before cleaning: {len(df)}")
df = df.dropna()
print(f"Records after removing NaN: {len(df)}")

# === 3. Data Exploration ===
print("\n=== DATA EXPLORATION ===")
print("Dataset Info:")
print(f"Shape: {df.shape}")
print(f"Date range: {df['DateTime'].min()} to {df['DateTime'].max()}")
print(f"Cities: {df['City'].unique()}")

print("\nPM2.5 Statistics by City:")
city_stats = df.groupby('City')['PM2.5 (µg/m³)'].agg(['count', 'mean', 'std', 'min', 'max'])
print(city_stats)

print("\nPM10 Statistics by City:")
city_stats_pm10 = df.groupby('City')['PM10 (µg/m³)'].agg(['count', 'mean', 'std', 'min', 'max'])
print(city_stats_pm10)

# === 4. Feature Engineering ===
features = ["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)",
            "Wind Direction (°)", "Pressure (hPa)", "Dust (µg/m³)", 
            "Aerosol Optical Depth", "Hour", "DayOfWeek", "Month", "Season"]

# One-hot encode city
city_dummies = pd.get_dummies(df['City'], prefix='City')
feature_df = pd.concat([df[features], city_dummies], axis=1)

print(f"\nTotal features after engineering: {len(feature_df.columns)}")

# === 5. Multiple Models Comparison ===
X = feature_df
y_pm25 = df["PM2.5 (µg/m³)"]
y_pm10 = df["PM10 (µg/m³)"]

# Split data
X_train, X_test, y_train_pm25, y_test_pm25 = train_test_split(X, y_pm25, test_size=0.3, random_state=42)
_, _, y_train_pm10, y_test_pm10 = train_test_split(X, y_pm10, test_size=0.3, random_state=42)

print("\n=== MODEL COMPARISON FOR PM2.5 ===")

models = {
    'Random Forest': RandomForestRegressor(n_estimators=200, random_state=42),
    'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, random_state=42),
    'Ridge Regression': Ridge(alpha=1.0),
    'Lasso Regression': Lasso(alpha=1.0),
}

results_pm25 = {}
results_pm10 = {}

for name, model in models.items():
    print(f"\nTraining {name}...")
    
    # PM2.5 model
    model.fit(X_train, y_train_pm25)
    y_pred_pm25 = model.predict(X_test)
    
    mae_pm25 = mean_absolute_error(y_test_pm25, y_pred_pm25)
    rmse_pm25 = np.sqrt(mean_squared_error(y_test_pm25, y_pred_pm25))
    r2_pm25 = r2_score(y_test_pm25, y_pred_pm25)
    
    # Cross-validation
    cv_scores_pm25 = cross_val_score(model, X_train, y_train_pm25, cv=5, scoring='r2')
    
    results_pm25[name] = {
        'MAE': mae_pm25,
        'RMSE': rmse_pm25,
        'R²': r2_pm25,
        'CV_R²_mean': cv_scores_pm25.mean(),
        'CV_R²_std': cv_scores_pm25.std()
    }
    
    print(f"{name} PM2.5 - MAE: {mae_pm25:.2f}, RMSE: {rmse_pm25:.2f}, R²: {r2_pm25:.3f}")
    print(f"CV R² Score: {cv_scores_pm25.mean():.3f} ± {cv_scores_pm25.std():.3f}")

# === 6. Feature Importance Analysis ===
print("\n=== FEATURE IMPORTANCE ANALYSIS ===")
rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
rf_model.fit(X_train, y_train_pm25)

feature_importance = pd.DataFrame({
    'feature': X_train.columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("Top 10 Most Important Features for PM2.5:")
print(feature_importance.head(10))

# === 7. Model Optimization ===
print("\n=== HYPERPARAMETER OPTIMIZATION ===")
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

grid_search = GridSearchCV(
    RandomForestRegressor(random_state=42),
    param_grid,
    cv=3,
    scoring='r2',
    n_jobs=-1,
    verbose=1
)

print("Running grid search (this may take a while)...")
grid_search.fit(X_train, y_train_pm25)

print(f"Best parameters: {grid_search.best_params_}")
print(f"Best CV score: {grid_search.best_score_:.3f}")

# Test optimized model
best_model = grid_search.best_estimator_
y_pred_optimized = best_model.predict(X_test)

mae_opt = mean_absolute_error(y_test_pm25, y_pred_optimized)
rmse_opt = np.sqrt(mean_squared_error(y_test_pm25, y_pred_optimized))
r2_opt = r2_score(y_test_pm25, y_pred_optimized)

print(f"\nOptimized Model Performance:")
print(f"MAE: {mae_opt:.2f}")
print(f"RMSE: {rmse_opt:.2f}")
print(f"R²: {r2_opt:.3f}")

# === 8. Residual Analysis ===
print("\n=== RESIDUAL ANALYSIS ===")
residuals = y_test_pm25 - y_pred_optimized

# Normality test
shapiro_stat, shapiro_p = stats.shapiro(residuals[:5000])  # Shapiro-Wilk test (limited to 5000 samples)
print(f"Shapiro-Wilk test for residuals normality: p-value = {shapiro_p:.6f}")
if shapiro_p > 0.05:
    print("Residuals appear to be normally distributed (good!)")
else:
    print("Residuals may not be normally distributed")

# Homoscedasticity check
correlation_pred_residuals = np.corrcoef(y_pred_optimized, np.abs(residuals))[0,1]
print(f"Correlation between predictions and absolute residuals: {correlation_pred_residuals:.3f}")
if abs(correlation_pred_residuals) < 0.1:
    print("Good: Low correlation suggests homoscedasticity")
else:
    print("Warning: High correlation suggests heteroscedasticity")

# === 9. Predictions Summary ===
print("\n=== PREDICTION SUMMARY ===")
print(f"Mean actual PM2.5: {y_test_pm25.mean():.2f} µg/m³")
print(f"Mean predicted PM2.5: {y_pred_optimized.mean():.2f} µg/m³")
print(f"Prediction error (MAE): {mae_opt:.2f} µg/m³ ({(mae_opt/y_test_pm25.mean()*100):.1f}% of mean)")

# Quality assessment based on EPA standards
def assess_prediction_quality(mae, mean_value):
    error_percentage = (mae / mean_value) * 100
    if error_percentage < 10:
        return "Excellent"
    elif error_percentage < 20:
        return "Good"
    elif error_percentage < 30:
        return "Fair"
    else:
        return "Poor"

quality = assess_prediction_quality(mae_opt, y_test_pm25.mean())
print(f"Model quality assessment: {quality}")

print("\n=== ANALYSIS COMPLETE ===")