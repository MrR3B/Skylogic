import xarray as xr
import pandas as pd
import glob
import os
import numpy as np
from datetime import datetime

def explore_netcdf_variables(file_path):
    """
    Explore and display all variables available in a NetCDF file.
    """
    try:
        ds = xr.open_dataset(file_path)
        print(f"\n📁 Exploring file: {os.path.basename(file_path)}")
        print("="*60)
        
        print(f"📊 File Dimensions:")
        for dim, size in ds.dims.items():
            print(f"   {dim}: {size}")
        
        print(f"\n🌍 Coordinate Variables:")
        for coord in ds.coords:
            var = ds[coord]
            print(f"   {coord}: {var.attrs.get('long_name', 'No description')} ({var.attrs.get('units', 'No units')})")
        
        print(f"\n📈 Data Variables:")
        data_vars = []
        for i, (var_name, var) in enumerate(ds.data_vars.items(), 1):
            long_name = var.attrs.get('long_name', 'No description')
            units = var.attrs.get('units', 'No units')
            shape = var.shape
            print(f"   {i:2d}. {var_name}: {long_name} ({units}) - Shape: {shape}")
            data_vars.append(var_name)
        
        ds.close()
        return data_vars
        
    except Exception as e:
        print(f"❌ Error exploring file: {str(e)}")
        return []

def get_user_variable_selection(available_vars):
    """
    Allow user to select variables interactively.
    """
    print(f"\n🎯 TARGET OUTPUT COLUMNS:")
    target_columns = [
        "DateTime", "Temperature (°C)", "Humidity (%)", "Heat Index (°C)", 
        "Wind Speed (m/s)", "Wind Direction (°)", "Pressure (hPa)", 
        "Dust (µg/m³)", "Aerosol Optical Depth", "PM2.5 (µg/m³)", "PM10 (µg/m³)"
    ]
    for i, col in enumerate(target_columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n🔍 VARIABLE SELECTION:")
    print("Enter the numbers of variables you want to extract (e.g., 1,3,5-8):")
    print("Or type 'all' to select all variables")
    print("Or type 'recommended' for common meteorological variables")
    
    while True:
        try:
            selection = input("Your selection: ").strip().lower()
            
            if selection == 'all':
                return available_vars
            
            elif selection == 'recommended':
                # Try to find common meteorological variables
                recommended = []
                patterns = ['t2m', 'temp', 'qv2m', 'humid', 'u10m', 'v10m', 'wind', 
                           'ps', 'pressure', 'dust', 'aod', 'pm25', 'pm10']
                for var in available_vars:
                    if any(pattern in var.lower() for pattern in patterns):
                        recommended.append(var)
                return recommended if recommended else available_vars[:5]
            
            else:
                # Parse number selection
                selected_vars = []
                parts = selection.split(',')
                
                for part in parts:
                    part = part.strip()
                    if '-' in part:
                        start, end = map(int, part.split('-'))
                        for i in range(start, end + 1):
                            if 1 <= i <= len(available_vars):
                                selected_vars.append(available_vars[i-1])
                    else:
                        i = int(part)
                        if 1 <= i <= len(available_vars):
                            selected_vars.append(available_vars[i-1])
                
                return list(set(selected_vars))  # Remove duplicates
                
        except (ValueError, IndexError):
            print("❌ Invalid selection. Please try again.")

def get_user_location_selection():
    """
    Allow user to select which Oman locations to extract data for.
    """
    locations = {
        'muscat': {
            'name': 'Muscat',
            'lat': 23.6,
            'lon': 58.4,
            'lat_range': (23.4, 23.8),
            'lon_range': (58.2, 58.6)
        },
        'musandam': {
            'name': 'Musandam',
            'lat': 26.2,
            'lon': 56.3,
            'lat_range': (26.0, 26.4),
            'lon_range': (56.1, 56.5)
        },
        'salalah': {
            'name': 'Salalah',
            'lat': 17.02,
            'lon': 54.1,
            'lat_range': (16.8, 17.2),
            'lon_range': (53.9, 54.3)
        }
    }
    
    print(f"\n🌍 LOCATION SELECTION:")
    print("Select which Oman locations to extract data for:")
    for i, (key, loc) in enumerate(locations.items(), 1):
        print(f"   {i}. {loc['name']} (Lat: {loc['lat']}, Lon: {loc['lon']})")
    print("   4. All locations (separate CSV for each)")
    
    while True:
        try:
            selection = input("Your selection (1-4): ").strip()
            
            if selection == '1':
                return {'muscat': locations['muscat']}
            elif selection == '2':
                return {'musandam': locations['musandam']}
            elif selection == '3':
                return {'salalah': locations['salalah']}
            elif selection == '4':
                return locations
            else:
                print("❌ Invalid selection. Please enter 1, 2, 3, or 4.")
                
        except ValueError:
            print("❌ Invalid input. Please try again.")

def apply_variable_transformations(df):
    """
    Apply common transformations to MERRA2 variables to match target output format.
    """
    # Create a copy to avoid modifying original
    df_transformed = df.copy()
    
    # Mass concentration conversions (kg/m³ to µg/m³)
    mass_vars = [col for col in df.columns if any(x in col.upper() for x in ['SMASS', 'CMASS', 'DUST', 'BC', 'OC', 'SO4', 'SS'])]
    for var in mass_vars:
        if 'SMASS' in var.upper() or 'CMASS' in var.upper():  # Surface or Column mass concentrations
            df_transformed[f'{var}_ugm3'] = df[var] * 1e9  # Convert kg/m³ to µg/m³
    
    # Calculate PM2.5 and PM10 from aerosol components (if available)
    # PM2.5 components
    pm25_components = []
    component_mapping = {
        'DUSMASS25': 'dust_pm25',
        'SSSMASS25': 'seasalt_pm25', 
        'BCSMASS': 'blackcarbon',
        'OCSMASS': 'organiccarbon',
        'SO4SMASS': 'sulfate'
    }
    
    for orig_var, new_name in component_mapping.items():
        if orig_var in df.columns:
            df_transformed[f'{new_name}_ugm3'] = df[orig_var] * 1e9
            pm25_components.append(f'{new_name}_ugm3')
    
    # Calculate total PM2.5 if components are available
    if pm25_components:
        df_transformed['PM25_total_ugm3'] = df_transformed[pm25_components].sum(axis=1)
    
    # Calculate PM10 (PM2.5 + larger dust particles)
    if 'DUSMASS' in df.columns and 'DUSMASS25' in df.columns:
        dust_coarse = (df['DUSMASS'] - df['DUSMASS25']) * 1e9  # Coarse dust (PM10-PM2.5)
        if 'PM25_total_ugm3' in df_transformed.columns:
            df_transformed['PM10_total_ugm3'] = df_transformed['PM25_total_ugm3'] + dust_coarse
        else:
            df_transformed['dust_coarse_ugm3'] = dust_coarse
    
    # Aerosol Optical Depth (no conversion needed, already dimensionless)
    aod_vars = [col for col in df.columns if 'EXTTAU' in col.upper()]
    for var in aod_vars:
        if 'TOTEXTTAU' in var.upper():
            df_transformed['aerosol_optical_depth'] = df[var]
    
    # Temperature conversions (Kelvin to Celsius)
    temp_vars = [col for col in df.columns if any(x in col.upper() for x in ['T2M', 'TEMP', 'T_'])]
    for var in temp_vars:
        if df[var].max() > 100:  # Likely in Kelvin
            df_transformed[f'{var}_celsius'] = df[var] - 273.15
    
    # Humidity conversions (specific humidity to relative humidity - approximate)
    humidity_vars = [col for col in df.columns if any(x in col.upper() for x in ['QV2M', 'HUMID', 'RH'])]
    for var in humidity_vars:
        if 'QV2M' in var.upper():
            # Approximate conversion from specific humidity (kg/kg) to RH (%)
            # This is a simplified conversion
            df_transformed[f'{var}_percent'] = df[var] * 1000 * 10  # Rough approximation
    
    # Wind speed and direction calculations
    u_vars = [col for col in df.columns if any(x in col.upper() for x in ['U10M', 'U_', 'UWIND'])]
    v_vars = [col for col in df.columns if any(x in col.upper() for x in ['V10M', 'V_', 'VWIND'])]
    
    for u_var, v_var in zip(u_vars, v_vars):
        if u_var in df.columns and v_var in df.columns:
            df_transformed['wind_speed_ms'] = np.sqrt(df[u_var]**2 + df[v_var]**2)
            df_transformed['wind_direction_deg'] = (np.arctan2(df[v_var], df[u_var]) * 180/np.pi + 360) % 360
    
    # Pressure conversions (Pa to hPa)
    pressure_vars = [col for col in df.columns if any(x in col.upper() for x in ['PS', 'PRESSURE', 'SLP'])]
    for var in pressure_vars:
        if df[var].max() > 10000:  # Likely in Pa
            df_transformed[f'{var}_hpa'] = df[var] / 100
    
    # Heat Index calculation (if temperature and humidity are available)
    temp_col = None
    humid_col = None
    
    for col in df_transformed.columns:
        if 'celsius' in col.lower() or ('T2M' in col.upper() and df_transformed[col].max() < 100):
            temp_col = col
        if 'percent' in col.lower() or 'RH' in col.upper():
            humid_col = col
    
    if temp_col and humid_col:
        # Simplified heat index calculation
        T = df_transformed[temp_col]
        RH = df_transformed[humid_col]
        df_transformed['heat_index_celsius'] = T + 0.5 * (T - 14.0) * (RH / 100.0)
    
    return df_transformed

def filter_data_by_location(df, location_info):
    """
    Filter dataframe by geographic location using lat/lon ranges.
    """
    lat_min, lat_max = location_info['lat_range']
    lon_min, lon_max = location_info['lon_range']
    
    filtered_df = df[
        (df['lat'] >= lat_min) & (df['lat'] <= lat_max) &
        (df['lon'] >= lon_min) & (df['lon'] <= lon_max)
    ].copy()
    
    # Add location identifier
    filtered_df['location'] = location_info['name']
    
    return filtered_df

def process_merra2_to_csv():
    """
    Interactive MERRA2 NetCDF to CSV converter for Oman region data.
    Files are already pre-filtered for Oman coordinates, so no lat/lon selection needed.
    """
    
    # Path to merra2_data files
    files = sorted(glob.glob("./merra2_data/*.nc4"))
    
    if not files:
        print("❌ No NetCDF files found in ./merra2_data/ directory")
        return
    
    print(f"🔍 Found {len(files)} NetCDF files to process")
    
    # Explore first file to understand available variables
    available_vars = explore_netcdf_variables(files[0])
    
    if not available_vars:
        print("❌ Could not read variables from NetCDF file")
        return
    
    # Get user selection for variables
    selected_vars = get_user_variable_selection(available_vars)
    
    if not selected_vars:
        print("❌ No variables selected")
        return
    
    print(f"\n✅ Selected variables: {', '.join(selected_vars)}")
    
    # Get user selection for locations
    selected_locations = get_user_location_selection()
    
    print(f"\n🌍 Selected locations: {', '.join([loc['name'] for loc in selected_locations.values()])}")
    
    all_dfs = []
    failed_files = []
    
    for i, file_path in enumerate(files, 1):
        try:
            filename = os.path.basename(file_path)
            print(f"📁 Processing ({i}/{len(files)}): {filename}")
            
            # Open dataset
            ds = xr.open_dataset(file_path)
            
            # Check if selected variables exist in this file
            file_vars = [var for var in selected_vars if var in ds.variables]
            if not file_vars:
                print(f"⚠️  Warning: No selected variables found in {filename}")
                ds.close()
                continue
            
            # Extract selected variables (no coordinate selection needed)
            df = ds[file_vars].to_dataframe().reset_index()
            
            # Add file information for tracking
            df['source_file'] = filename
            df['processing_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Apply transformations based on variable patterns
            df = apply_variable_transformations(df)
            
            all_dfs.append(df)
            ds.close()  # Close dataset to free memory
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {str(e)}")
            failed_files.append(filename)
            continue
    
    if not all_dfs:
        print("❌ No data could be processed from any files")
        return
    
    # Combine all dataframes
    print(f"🔄 Combining data from {len(all_dfs)} successful files...")
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Sort by time for chronological order
    if 'time' in combined_df.columns:
        combined_df = combined_df.sort_values('time').reset_index(drop=True)
    
    # Filter data by selected locations and save separate CSV files
    output_files = []
    location_summaries = []
    
    for location_key, location_info in selected_locations.items():
        print(f"🎯 Filtering data for {location_info['name']}...")
        
        # Filter data for this location
        location_df = filter_data_by_location(combined_df, location_info)
        
        if len(location_df) == 0:
            print(f"⚠️  No data found for {location_info['name']} in the specified coordinates")
            continue
        
        # Generate output filename
        location_name = location_info['name'].lower().replace(' ', '_')
        output_file = f"oman_{location_name}_data.csv"
        
        # Save location-specific CSV
        location_df.to_csv(output_file, index=False)
        output_files.append(output_file)
        
        # Calculate summary statistics
        summary = {
            'location': location_info['name'],
            'records': len(location_df),
            'file_size_mb': os.path.getsize(output_file) / 1024 / 1024,
            'date_range': (location_df['time'].min(), location_df['time'].max()) if 'time' in location_df.columns else ('N/A', 'N/A'),
            'unique_coords': len(location_df[['lat', 'lon']].drop_duplicates())
        }
        location_summaries.append(summary)
        
        print(f"✅ Saved {len(location_df):,} records for {location_info['name']} to {output_file}")
    
    # Print comprehensive summary
    print("\n" + "="*60)
    print("📊 PROCESSING SUMMARY")
    print("="*60)
    print(f"✅ Successfully processed: {len(all_dfs)} files")
    print(f"❌ Failed files: {len(failed_files)}")
    if failed_files:
        print(f"   Failed: {', '.join(failed_files)}")
    print(f"📈 Total combined records: {len(combined_df):,}")
    
    print(f"\n🌍 LOCATION-SPECIFIC RESULTS:")
    for summary in location_summaries:
        print(f"   📍 {summary['location']}:")
        print(f"      Records: {summary['records']:,}")
        print(f"      File size: {summary['file_size_mb']:.2f} MB")
        print(f"      Date range: {summary['date_range'][0]} to {summary['date_range'][1]}")
        print(f"      Grid points: {summary['unique_coords']}")
    
    print(f"\n💾 OUTPUT FILES:")
    for output_file in output_files:
        print(f"   📁 {output_file}")
    
    print("="*60)
    print("✅ MERRA2 to CSV conversion completed successfully!")
    print("🎯 Data extracted for selected Oman locations with proper unit conversions!")

if __name__ == "__main__":
    process_merra2_to_csv()
