import os
import csv
import rasterio
import numpy as np
import matplotlib.pyplot as plt
import logging
import sys
from datetime import datetime

handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush  # Ensure flush method is called on each log entry
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

images_label = os.getenv("images")
cloud_label = os.getenv("cloud")
ndvi_label = os.getenv("ndvi")
cloud_coverage_threshold_str = os.getenv("cloud_coverage_threshold")
cloud_coverage_threshold = float(str(cloud_coverage_threshold_str))

images_dir = "/cfs"+str(images_label)
cloud_dir = "/cfs"+str(cloud_label)
ndvi_output_dir = "/cfs"+str(ndvi_label)
csv_file_path = os.path.join(cloud_dir, 'cloud_coverage.csv')

if not os.path.exists(ndvi_output_dir):
    os.makedirs(ndvi_output_dir)
    print(f"Created directory: {ndvi_output_dir}")

filtered_files = []

with open(csv_file_path, mode='r') as csv_file:
    reader = csv.DictReader(csv_file)
    
    for row in reader:
        filename = row['filename']
        cloud_coverage_percentage = float(row['cloud_coverage_percentage'])
        
        if cloud_coverage_percentage < cloud_coverage_threshold:
            try:
                date_str = filename.split('out_')[1].replace('.tif', '')
                date = datetime.strptime(date_str, "%Y_%m_%dT%H_%M_%S")
                filtered_files.append((filename, date))
            except Exception as e:
                print(f"Error parsing date from filename {filename}: {e}")

def read_bands(file_path):
    with rasterio.open(file_path) as src:
        red_band = src.read(1)  # Assuming B04 is the first band
        nir_band = src.read(4)  # Assuming B08 is the fourth band
    return red_band, nir_band

def calculate_ndvi(nir_band, red_band):
    ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band.astype(float) + red_band.astype(float) + 1e-10)  # Avoid division by zero
    return ndvi

average_ndvi_values = []
dates = []
csv_data = []

for filename, date in filtered_files:
    file_path = os.path.join(images_dir, filename)
    red_band, nir_band = read_bands(file_path)
    ndvi = calculate_ndvi(nir_band, red_band)
    average_ndvi = np.nanmean(ndvi)
    average_ndvi_values.append(average_ndvi)
    dates.append(date)
    csv_data.append({'date': date.strftime("%Y-%m-%d %H:%M:%S"), 'filename': filename, 'ndvi': average_ndvi})

csv_output_file = os.path.join(ndvi_output_dir, 'ndvi_time_series.csv')
with open(csv_output_file, mode='w', newline='') as csv_file:
    fieldnames = ['date', 'filename', 'ndvi']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(csv_data)

print(f"CSV file with time series data saved to: {csv_output_file}")

if len(dates) > 0 and len(average_ndvi_values) > 0:
    sorted_data = sorted(zip(dates, average_ndvi_values))
    dates, average_ndvi_values = zip(*sorted_data)

    plt.figure(figsize=(10, 6))
    plt.plot(dates, average_ndvi_values, marker='o', linestyle='-', color='green')
    plt.xlabel('Date')
    plt.ylabel('Average NDVI')
    plt.title('Average NDVI Time Series for Filtered Files (Cloud Coverage < 30%)')
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plot_output_file = os.path.join(ndvi_output_dir, 'ndvi_time_series.png')
    plt.savefig(plot_output_file)
    print(f"Time series plot saved to: {plot_output_file}")

    plt.show()

else:
    print("No valid files with dates or NDVI values for plotting.")
