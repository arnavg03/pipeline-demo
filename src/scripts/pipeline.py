import paramiko
import boto3
import xarray as xr
import rioxarray
import os
import matplotlib.pyplot as plt
from pathlib import Path

# File paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LOCAL_FILE = PROJECT_ROOT / "data" / "raw_data.nc"
KEY_FILE = PROJECT_ROOT / "sftp-key"
tif_filename = PROJECT_ROOT / "data" / "latest_tmax.tif"
png_filename = PROJECT_ROOT / "data" / "tmax_qc_plot.png"

#  Env variables
RAW_BUCKET = os.getenv("RAW_BUCKET")         
PROCESSED_BUCKET = os.getenv("PROCESSED_BUCKET") 
SFTP_HOST = os.getenv("SFTP_HOST") 
SFTP_USER = os.getenv("SFTP_USER")

# Upload raw data to S3 via AWS SFTP
print("Authenticating with AWS SFTP...")
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

mykey = paramiko.RSAKey.from_private_key_file(KEY_FILE)
ssh.connect(hostname=SFTP_HOST, username=SFTP_USER, pkey=mykey)

print("Transferring file through SFTP tunnel to S3 Data Lake...")
sftp = ssh.open_sftp()
sftp.put(LOCAL_FILE, f"/{RAW_BUCKET}/raw_data.nc")
sftp.close()
ssh.close()

# Data Analysis
print("Processing multi-dimensional array...")
ds = xr.open_dataset(LOCAL_FILE, engine='netcdf4')
latest_temp = ds['tmax'].isel(time=-1)

#fix for map wrapping from analysis.ipynb
latest_temp.coords['lon'] = (latest_temp.coords['lon'] + 180) % 360 - 180
latest_temp = latest_temp.sortby(latest_temp.lon)

latest_temp = latest_temp.rio.write_crs("epsg:4326")
latest_temp = latest_temp.rename({'lat': 'y', 'lon': 'x'})

# Exportin to GeoTIFF (rioxarray)
print("Exporting to GeoTIFF...")
latest_temp.rio.to_raster(tif_filename)

# QC Viz 
print("Generating QC plot...")
latest_temp.plot(cmap='inferno')
date_str = latest_temp.time.dt.strftime('%Y-%m-%d').values
plt.title(f"Max Surface Temp (°C) on {date_str}")
plt.savefig(png_filename)

# Upload to S3 (boto3)
print("Uploading GeoTIFF and PNG to S3...")
s3 = boto3.client('s3')
s3.upload_file(tif_filename, PROCESSED_BUCKET, "geotiffs/latest_tmax.tif")
s3.upload_file(png_filename, PROCESSED_BUCKET, "qc_plots/tmax_qc_plot.png")

print("Pipeline Execution Complete - Processed data and QC plot uploaded to S3.")