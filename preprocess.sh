#!/bin/bash
echo "Starting Daily ETL Pipeline..."

# Using a reliable UCAR temperature dataset for the interview demo
DATA_URL="https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/tmax.2026.nc"
LOCAL_FILE="raw_data.nc"

echo "1. Fetching daily NetCDF data from upstream source (NOAA)..."
curl -s -o $LOCAL_FILE $DATA_URL

# Basic Data Validation
if [ -s "$LOCAL_FILE" ]; then
    echo "Validation Passed: $LOCAL_FILE downloaded successfully."
    echo "2. Handing off to Python for spatial processing..."
    python pipeline.py
else
    echo "Validation Failed: Data stream is empty or unreachable."
    exit 1
fi