import earthaccess

auth = earthaccess.login(persist=True)
results = earthaccess.search_data(
    short_name="M2I1NXASM", # اسم المنتج
    cloud_hosted=True,
    bounding_box=(51.5, 16.5, 60, 26), # حدود عمان (lon_min, lat_min, lon_max, lat_max)
    temporal=("2015-01-01", "2015-01-02") # مثال: يوم واحد
)
files = earthaccess.download(results, "./merra2_data/")
print("Downloaded files:", files)
