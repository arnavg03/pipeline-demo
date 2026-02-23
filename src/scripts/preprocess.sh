#!/bin/bash
echo "Starting Daily ETL Pipeline"

#fix: mkdir for data folder
mkdir -p data

DATA_URL="https://downloads.psl.noaa.gov/Datasets/cpc_global_temp/tmax.2026.nc"
LOCAL_FILE="data/raw_data.nc"

echo "Fetching daily NetCDF data..."
curl -s -o $LOCAL_FILE $DATA_URL

if [ -s "$LOCAL_FILE" ]; then
    echo "Validation Passed: File downloaded."
    # Run the Python script
    python src/scripts/pipeline.py
else
    echo "Validation Failed: File empty."
    exit 1
fi