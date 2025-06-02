# solar-pv-analysis
# Overview
This project analyzes solar photovoltaic (PV) system performance by examining the relationship between Performance Ratio (PR) and Global Horizontal Irradiance (GHI) over time.
# Dataset

Time Period: July 2019 - March 2022
Total Data Points: 982
# Parameters:

Performance Ratio (PR) - measures actual vs expected energy output
Global Horizontal Irradiance (GHI) - solar radiation measurement



# Analysis Features

Performance tracking with 30-day moving averages
GHI-based color coding for data visualization
Budget line calculation (starts at 73.9%, decreases 0.8% annually)
Statistical summaries for recent performance periods

# Files

processed_solar_data.csv - Combined dataset with all measurements
pr_analysis_graph.png - Main visualization showing PR trends
main.py - Data processing and visualization code

# Key Findings
The analysis reveals performance patterns and identifies periods where actual performance exceeded budget expectations. Color-coded scatter points help visualize the correlation between solar irradiance levels and system performance.
# Usage
bashpython main.py
Output files will be generated in the same directory.
