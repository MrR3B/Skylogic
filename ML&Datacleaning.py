import pandas as pd
import glob
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

# === 1. Load and merge all CSVs ===
files = glob.glob("./data/*.csv")  # ضع ملفات مسقط/مسندم/صلالة داخل مجلد data
df_list = [pd.read_csv(f) for f in files]
df = pd.concat(df_list, ignore_index=True)

# === 2. Data cleaning ===
# إصلاح أسماء الأعمدة (إزالة الرموز الغريبة مثل Â)
df.columns = [c.replace("Â", "").strip() for c in df.columns]

# تحويل التاريخ إلى نوع datetime
df["DateTime"] = pd.to_datetime(df["DateTime"])

# حذف العمود المشتق Heat Index
if "Heat Index (°C)" in df.columns:
    df = df.drop(columns=["Heat Index (°C)"])

# إزالة القيم المفقودة
df = df.dropna()

# === 3. Features and Target ===
features = ["Temperature (°C)", "Humidity (%)", "Wind Speed (m/s)",
            "Wind Direction (°)", "Pressure (hPa)", "Dust (µg/m³)", "Aerosol Optical Depth"]

X = df[features]
y = df["PM2.5 (µg/m³)"]  # ممكن تغيّرها لـ PM10

# === 4. Train-Test Split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# === 5. Train Model ===
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# === 6. Evaluate ===
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("Model Performance:")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²: {r2:.2f}")
