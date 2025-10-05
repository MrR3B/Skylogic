# Simple test to verify alert functionality
library(shiny)
library(shinydashboard)

# Test the alert functions
source("enhanced_aviation_dashboard.R", local = TRUE)

# Test data
test_data <- data.frame(
  site = c("Muscat", "Salalah", "Musandam"),
  pm25 = c(65, 25, 15),
  pm10 = c(120, 45, 30),
  wind_speed = c(30, 12, 8),
  dust = c(150, 80, 40),
  stringsAsFactors = FALSE
)

# Calculate visibility and flight safety
test_data$visibility <- calc_visibility(test_data$pm25, test_data$pm10, test_data$dust)
test_data$AQI <- calc_overall_aqi(test_data$pm25, test_data$pm10)
test_data$flight_safety_score <- calc_flight_safety_score(
  test_data$pm25, test_data$pm10, test_data$wind_speed, 
  test_data$dust, test_data$visibility
)

# Add alert levels
test_data$alert_level <- case_when(
  test_data$AQI > 150 | test_data$flight_safety_score < 0.4 ~ "HIGH",
  test_data$AQI > 100 | test_data$flight_safety_score < 0.6 ~ "MODERATE", 
  TRUE ~ "GOOD"
)

# Print results
cat("=== FLIGHT SAFETY TEST RESULTS ===\n")
for(i in 1:nrow(test_data)) {
  row <- test_data[i,]
  cat(sprintf("📍 %s:\n", row$site))
  cat(sprintf("  AQI: %d\n", round(row$AQI)))
  cat(sprintf("  Visibility: %.1f km\n", row$visibility))
  cat(sprintf("  Flight Safety: %d%%\n", round(row$flight_safety_score * 100)))
  cat(sprintf("  Alert Level: %s\n", row$alert_level))
  cat("---\n")
}

cat("\n=== ALERT SUMMARY ===\n")
high_alerts <- sum(test_data$alert_level == "HIGH")
moderate_alerts <- sum(test_data$alert_level == "MODERATE")
good_alerts <- sum(test_data$alert_level == "GOOD")

cat(sprintf("🚨 HIGH RISK: %d locations\n", high_alerts))
cat(sprintf("⚠️ MODERATE RISK: %d locations\n", moderate_alerts))
cat(sprintf("✅ GOOD CONDITIONS: %d locations\n", good_alerts))

cat("\n=== AVIATION ALERTS ===\n")
critical_flight <- test_data[test_data$flight_safety_score < 0.4,]
poor_flight <- test_data[test_data$flight_safety_score >= 0.4 & test_data$flight_safety_score < 0.7,]
good_flight <- test_data[test_data$flight_safety_score >= 0.7,]

if(nrow(critical_flight) > 0) {
  cat("🚫 NO-FLY CONDITIONS:\n")
  for(i in 1:nrow(critical_flight)) {
    row <- critical_flight[i,]
    cat(sprintf("📍 %s: Visibility %.1fkm | Safety %d%%\n", 
                row$site, row$visibility, round(row$flight_safety_score * 100)))
  }
}

if(nrow(poor_flight) > 0) {
  cat("⚠️ CAUTION REQUIRED:\n")
  for(i in 1:nrow(poor_flight)) {
    row <- poor_flight[i,]
    cat(sprintf("📍 %s: Visibility %.1fkm | Safety %d%%\n", 
                row$site, row$visibility, round(row$flight_safety_score * 100)))
  }
}

if(nrow(good_flight) > 0) {
  cat("✅ GOOD FLIGHT CONDITIONS:\n")
  for(i in 1:nrow(good_flight)) {
    row <- good_flight[i,]
    cat(sprintf("📍 %s: Visibility %.1fkm | Safety %d%%\n", 
                row$site, row$visibility, round(row$flight_safety_score * 100)))
  }
}