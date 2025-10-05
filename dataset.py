import xarray as xr
import pandas as pd
import numpy as np

# افتح الملف
ds = xr.open_dataset("MERRA2_400.inst1_2d_asm_Nx.20150101.nc4")

# حدود عمان
lat_min, lat_max = 16.5, 26.5
lon_min, lon_max = 52.0, 60.5

# قص الداتا على عمان
oman_data = ds.sel(lat=slice(lat_min, lat_max), lon=slice(lon_min, lon_max))

# نحول لجدول
df = oman_data.to_dataframe().reset_index()

# نحسب سرعة الرياح ودرجة الحرارة بالمئوية
if "U10M" in df and "V10M" in df:
    df["WindSpeed10M"] = np.sqrt(df["U10M"]**2 + df["V10M"]**2)
if "T2M" in df:
    df["T2M_C"] = df["T2M"] - 273.15

# حفظ لملف CSV
df.to_csv("oman_20150101.csv", index=False)

print("تم استخراج بيانات عمان ليوم 2015-01-01 ✅")
print(df.head())
