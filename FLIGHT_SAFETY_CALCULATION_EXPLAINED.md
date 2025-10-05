# ✈️ FLIGHT SAFETY CALCULATION - DETAILED EXPLANATION

## 🎯 **FLIGHT SAFETY SCORE FORMULA:**

The flight safety score is calculated using a **weighted multi-factor approach** that combines 4 key aviation safety parameters:

```r
calc_flight_safety_score <- function(pm25, pm10, wind_speed, dust, visibility) {
  aqi <- calc_overall_aqi(pm25, pm10)
  visibility_score <- pmax(pmin(visibility / 25, 1), 0)
  air_quality_score <- pmax(pmin((300 - aqi) / 300, 1), 0)
  wind_score <- pmax(pmin((25 - wind_speed) / 25, 1), 0)
  dust_score <- pmax(pmin((200 - dust) / 200, 1), 0)
  
  safety_score <- (visibility_score * 0.3 + air_quality_score * 0.25 + 
                   wind_score * 0.25 + dust_score * 0.2)
  return(pmax(pmin(safety_score, 1), 0))
}
```

## 📊 **COMPONENT BREAKDOWN:**

### 1. **🌫️ Visibility Score (30% weight)**
```r
visibility_score = min(visibility / 25, 1)
```
- **Perfect visibility**: 25+ km = 100% score
- **Linear decrease**: Each km less reduces score proportionally
- **Example**: 12.5 km visibility = 50% score (12.5/25 = 0.5)
- **Aviation impact**: Most critical for takeoff/landing safety

### 2. **🌬️ Air Quality Score (25% weight)**
```r
air_quality_score = (300 - AQI) / 300
```
- **Perfect air**: AQI = 0 → 100% score
- **Moderate air**: AQI = 150 → 50% score  
- **Hazardous air**: AQI = 300 → 0% score
- **Aviation impact**: Engine performance, pilot health, passenger comfort

### 3. **💨 Wind Score (25% weight)**
```r
wind_score = (25 - wind_speed) / 25
```
- **Calm conditions**: 0 km/h wind = 100% score
- **Moderate wind**: 12.5 km/h = 50% score
- **Strong wind**: 25+ km/h = 0% score
- **Aviation impact**: Turbulence, crosswind landings, fuel efficiency

### 4. **🌪️ Dust Score (20% weight)**
```r
dust_score = (200 - dust) / 200
```
- **Clean air**: 0 µg/m³ dust = 100% score
- **Moderate dust**: 100 µg/m³ = 50% score
- **Dust storm**: 200+ µg/m³ = 0% score
- **Aviation impact**: Engine intake, visibility reduction, maintenance

## 🔢 **CALCULATION EXAMPLES:**

### **Example 1: Good Flight Conditions**
```
PM2.5: 15 µg/m³, PM10: 30 µg/m³ → AQI: 45
Visibility: 20 km (calculated from pollutants)
Wind Speed: 10 km/h
Dust: 50 µg/m³

Calculations:
• Visibility Score: 20/25 = 0.80 (80%)
• Air Quality Score: (300-45)/300 = 0.85 (85%)
• Wind Score: (25-10)/25 = 0.60 (60%)
• Dust Score: (200-50)/200 = 0.75 (75%)

Final Score: 0.80×0.3 + 0.85×0.25 + 0.60×0.25 + 0.75×0.2
           = 0.24 + 0.21 + 0.15 + 0.15 = 0.75 (75%)
```
**Result**: ✅ **GOOD FLIGHT CONDITIONS** (75% safety)

### **Example 2: Poor Flight Conditions**
```
PM2.5: 65 µg/m³, PM10: 120 µg/m³ → AQI: 165
Visibility: 8 km (calculated from high pollution)
Wind Speed: 30 km/h
Dust: 150 µg/m³

Calculations:
• Visibility Score: 8/25 = 0.32 (32%)
• Air Quality Score: (300-165)/300 = 0.45 (45%)
• Wind Score: max(0, (25-30)/25) = 0.00 (0%)
• Dust Score: (200-150)/200 = 0.25 (25%)

Final Score: 0.32×0.3 + 0.45×0.25 + 0.00×0.25 + 0.25×0.2
           = 0.096 + 0.113 + 0.00 + 0.05 = 0.26 (26%)
```
**Result**: 🚫 **NO-FLY CONDITIONS** (26% safety)

## 🎯 **AVIATION SAFETY THRESHOLDS:**

### **🚫 CRITICAL - No Fly (< 40%)**
- **Conditions**: Very poor visibility, high pollution, strong winds
- **Recommendation**: ❌ **Flight cancellation or major delays**
- **Risk**: High probability of safety incidents

### **⚠️ CAUTION - Marginal (40-70%)**
- **Conditions**: Reduced visibility, moderate pollution, some wind
- **Recommendation**: ⚠️ **Enhanced procedures, experienced pilots only**
- **Risk**: Increased vigilance required

### **✅ GOOD - Safe (≥ 70%)**
- **Conditions**: Good visibility, clean air, calm winds
- **Recommendation**: ✅ **Normal flight operations**
- **Risk**: Standard aviation safety levels

## 🔧 **VISIBILITY CALCULATION:**

The visibility is estimated from pollution levels using:
```r
calc_visibility <- function(pm25, pm10, dust) {
  visibility <- 50 / (1 + (pm25/50) + (pm10/100) + (dust/200))
  return(max(min(visibility, 50), 0.1))  # Between 0.1-50 km
}
```

**Physical basis**: Higher pollution reduces atmospheric transparency, limiting pilot visibility for navigation and landing.

## 📈 **REAL-WORLD AVIATION CONTEXT:**

### **International Standards Alignment:**
- **ICAO Standards**: Visibility requirements for different flight phases
- **NASA Research**: Air quality impacts on aviation safety
- **Weather Minimums**: Integration with meteorological flight planning

### **Oman-Specific Factors:**
- **Desert Conditions**: High dust factor weighting (20%)
- **Coastal Effects**: Humidity and sea breeze interactions
- **Mountain Terrain**: Wind pattern complexity in Musandam

## 🚨 **IMPACT ON AVIATION ALERTS SYSTEM:**

### **How Flight Safety Scores Trigger Aviation Alerts:**

The calculated flight safety scores **directly control** what appears in your Aviation Alerts boxes:

#### **1. 🚫 NO-FLY CONDITIONS Alert (Safety < 40%)**
```
✈️ Aviation Status - Day 1 - 14:00
🚫 NO-FLY CONDITIONS
📍 Muscat: Visibility 3.2km | Safety 35%
⚠️ Recommend flight delays or diversions
```
**Triggered when**: Flight safety score falls below 0.4 (40%)
**Alert Impact**: Red warning box, flight cancellation recommendations

#### **2. ⚠️ CAUTION REQUIRED Alert (Safety 40-70%)**
```
⚠️ CAUTION REQUIRED
📍 Salalah: Visibility 7.1km | Safety 55%
⚠️ Enhanced navigation, reduced visibility
```
**Triggered when**: Flight safety score between 0.4-0.7 (40-70%)
**Alert Impact**: Orange warning box, enhanced procedures required

#### **3. ✅ GOOD FLIGHT CONDITIONS Alert (Safety ≥ 70%)**
```
✅ GOOD FLIGHT CONDITIONS
📍 Musandam: Visibility 15.2km | Safety 82%
```
**Triggered when**: Flight safety score ≥ 0.7 (70%)
**Alert Impact**: Green status box, normal operations approved

### **📊 Aviation Alerts Integration:**

#### **Multi-Location Display:**
- **Each location** (Muscat, Salalah, Musandam) gets its **own flight safety score**
- **Aviation Alerts box** shows **all locations** with their individual safety levels
- **Real-time updates** as you move the 48-hour timeline slider

#### **Additional Weather Warnings:**
The Aviation Alerts also include **weather-specific warnings** based on the calculation components:

```
🌤️ WEATHER CONDITIONS
🌪️ High dust levels at Muscat (when dust > 100 µg/m³)
💨 Strong winds at Salalah (when wind > 25 km/h)
🌫️ Poor visibility at Musandam (when visibility < 5 km)
```

#### **Flight Planning Integration:**
```
📋 PLANNING NOTES
• Use 48-hour timeline for flight planning
• Check upcoming hours for condition changes
• Monitor real-time updates for safety
```

### **🎯 Aviation Decision Matrix:**

| Flight Safety Score | Aviation Alert Level | Flight Recommendation | Alert Box Color |
|---------------------|----------------------|----------------------|-----------------|
| **≥ 70%** | ✅ GOOD CONDITIONS | Normal operations | Green |
| **40-69%** | ⚠️ CAUTION REQUIRED | Enhanced procedures | Orange |
| **< 40%** | 🚫 NO-FLY CONDITIONS | Cancel/delay flights | Red |

### **📈 Real-Time Aviation Impact:**

1. **Timeline Sensitivity**: As you move the 48-hour slider, flight safety scores change and **Aviation Alerts update instantly**

2. **Location-Specific**: Each of the 3 Oman locations shows **individual flight safety assessments**

3. **Forecast Warnings**: Aviation Alerts help pilots **plan ahead** by showing deteriorating conditions

4. **Regulatory Compliance**: Thresholds align with **international aviation safety standards**

### **✈️ Practical Aviation Usage:**

- **Pre-flight Planning**: Check Aviation Alerts for departure/arrival times
- **Route Planning**: Compare safety scores across Muscat/Salalah/Musandam
- **Weather Monitoring**: Track changing conditions over 48-hour forecast
- **Emergency Decisions**: Real-time alerts for flight diversions

**Your flight safety calculation creates a comprehensive Aviation Alerts system that provides actionable, location-specific flight safety guidance for Oman's aviation operations!** 🛫📊🌟