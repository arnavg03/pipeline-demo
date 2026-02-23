# Weather Data Pipeline Project

This project is an automated ETL pipeline that pulls daily temperature data from NOAA and turns it into GeoTIFF files that can be used in mapping software like QGIS. I built it to solve the problem of NOAA's longitude coordinates being on a 0-360 scale, which breaks the standard map viz (clips continents off)

## What it does

1. **Fetch:** A shell script uses `curl` to download the latest NetCDF file from NOAA's servers (updates at ~9:30 am).
2. **Transfer:** The Python script uses an SFTP (AWS Transfer Family) tunnel to send that raw data into an AWS S3 bucket.
3. **Process:** Python (`xarray`) shifts the longitude so the map centers correctly and adds the `EPSG:4326` coordinate system so the file is spatially aware.
4. **Upload:** It saves a GeoTIFF (`rioxarray`) and a PNG plot back to a "clean" S3 bucket for analysis.

### The Stack

* **Cloud:** AWS (S3 for storage, EC2 compute for the server, IAM for roles and security, and Transfer Family for the SFTP gateway).
* **Language:** Python 3.9 (`os`, `xarray`, `rioxarray`, `boto3`, `rioxarray`, `matplotlib`, `pathlib` and `paramiko`).
* **DevOps:** Docker and a Linux Cron job to handle the daily scheduling.

### Problems Faced

* **Docker Image Issues:** I originally used a "slim" Python image but it didn't have the C++ libraries needed for mapping, so I had to switch to the full Python 3.9 base image.
* **Mac vs Cloud:** Since I'm on an M4 Mac and the server is Intel, the geospatial libraries wouldn't compile locally. I used the `--platform=linux/amd64` flag in Docker to fix this.
* **Permissions:** I had some `AssumeRole` errors in AWS. I had to update the IAM Trust Policy to allow the Transfer Family service to use the S3 access role.
* **Coordinate Math:** The NOAA data was center-aligned at the prime meridian but used 0-360. I wrote a math function `(lon + 180) % 360 - 180` to re-align it to the standard -180 to 180.

## How to Run Locally

You need a `.env` file with your AWS keys and S3 bucket names.

```bash
docker build --platform linux/amd64 -t pipeline-app .
docker run --rm --env-file .env pipeline-app

```

### Automation

On the EC2 server, I set up a crontab that runs the docker container every morning at 2:00 AM.

```bash
0 2 * * * cd /home/ec2-user/pipeline-demo && docker run --rm --env-file .env pipeline-app

```
