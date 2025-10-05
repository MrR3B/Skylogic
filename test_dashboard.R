# Test script to check if the dashboard runs without errors
library(shiny)
library(shinydashboard) 
library(leaflet)

# Check if the main dashboard file can be sourced
tryCatch({
  source("enhanced_aviation_dashboard.R")
  cat("Dashboard file loaded successfully!\n")
}, error = function(e) {
  cat("Error loading dashboard:", e$message, "\n")
})

# Try to run the app
cat("Attempting to run the dashboard...\n")
runApp(list(ui = ui, server = server), launch.browser = FALSE, host = "127.0.0.1", port = 3838)