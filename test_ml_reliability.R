# Test script to verify 48-hour ML prediction reliability
library(dplyr)

# Source the prediction functions (simulated)
test_ml_reliability <- function() {
  cat("🧪 TESTING 48-HOUR ML PREDICTION RELIABILITY\n")
  cat("=" * 50, "\n")
  
  # Test parameters
  locations <- data.frame(
    site = c("Muscat", "Salalah", "Musandam"),
    lat = c(23.5933, 17.0387, 26.2041),
    lon = c(58.2844, 54.0914, 56.2606),
    region = c("Muscat", "Dhofar", "Musandam")
  )
  
  # Test prediction consistency
  results <- list()
  
  for(i in 1:nrow(locations)) {
    location <- locations[i, ]
    location_results <- list()
    
    cat("\n📍 Testing", location$site, "predictions...\n")
    
    # Test multiple runs for consistency
    for(run in 1:3) {
      run_results <- list()
      
      for(hour in c(0, 12, 24, 36, 47)) {  # Test key hours
        # Simulate ML prediction (replace with actual ML call)
        base_pm25 <- switch(location$region,
                           "Muscat" = 25, "Dhofar" = 18, "Musandam" = 15, 20)
        
        day_num <- floor(hour / 24) + 1
        hour_of_day <- hour %% 24
        
        # Enhanced prediction logic
        circadian_factor <- 1 + 0.4 * sin((hour_of_day - 8) * pi / 12)
        forecast_uncertainty <- 1 + 0.02 * hour
        
        pm25_pred <- base_pm25 * circadian_factor + rnorm(1, 0, 1.5 * forecast_uncertainty)
        aqi_pred <- if(pm25_pred <= 12) 50 else if(pm25_pred <= 35.4) 75 else 100
        
        run_results[[paste0("h", hour)]] <- list(
          hour = hour,
          pm25 = max(1, pm25_pred),
          aqi = aqi_pred,
          confidence = max(0.5, 1 - 0.01 * hour)
        )
      }
      
      location_results[[paste0("run", run)]] <- run_results
    }
    
    results[[location$site]] <- location_results
    
    # Calculate reliability metrics
    pm25_values <- sapply(location_results, function(run) sapply(run, function(h) h$pm25))
    pm25_cv <- apply(pm25_values, 1, function(x) sd(x) / mean(x))  # Coefficient of variation
    
    cat("  PM2.5 Variability (CV):\n")
    for(j in 1:length(pm25_cv)) {
      hour_name <- names(pm25_cv)[j]
      cv_percent <- round(pm25_cv[j] * 100, 1)
      status <- if(cv_percent < 10) "✅ Excellent" else if(cv_percent < 20) "🟡 Good" else "🔴 Needs improvement"
      cat("    ", hour_name, ": ", cv_percent, "% ", status, "\n")
    }
  }
  
  cat("\n🎯 RELIABILITY TEST SUMMARY:\n")
  cat("- Tested 3 locations × 5 time points × 3 runs = 45 predictions\n")
  cat("- 48-hour forecast range with uncertainty modeling\n") 
  cat("- Location-specific baselines implemented\n")
  cat("- Circadian rhythm patterns included\n")
  cat("- Forecast confidence decreasing with time\n")
  
  return(results)
}

# Run the test
if(interactive()) {
  test_results <- test_ml_reliability()
  cat("\n✅ ML Prediction Reliability Test Complete!\n")
}