import os
import csv
import rasterio
import numpy as np
import logging
import sys
from PIL import Image
from pathlib import Path

handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush  # Ensure flush method is called on each log entry
logging.basicConfig(level=logging.INFO, handlers=[handler])
logger = logging.getLogger(__name__)

images_label = os.getenv("images")
cloud_label = os.getenv("cloud")

cloud_dir_path = "/cfs/"+str(cloud_label)
cloud_dir = Path(cloud_dir_path)
cloud_dir.mkdir(parents=True, exist_ok=True)
images_dir = "/cfs/"+str(images_label)
csv_file_path = os.path.join(cloud_dir, 'cloud_coverage.csv')

def read_bands(file_path, band_indices):
    with rasterio.open(file_path) as src:
        bands = src.read(band_indices)
    return bands

def generate_and_save_cloud_mask(file_path, output_tiff_path, output_jpeg_path):
    # Indices for B02, B03, B04, and B08 in the GeoTIFF
    b04_idx, b03_idx, b02_idx, b08_idx = 1, 2, 3, 4  # Update these indices as necessary

    # Read the necessary bands (B04=Red, B03=Green, B02=Blue, B08=NIR)
    bands = read_bands(file_path, [b04_idx, b03_idx, b02_idx, b08_idx])
    
    # Use the NIR band (B08) for cloud detection
    nir_band = bands[3]  # B08 (NIR)

    # Manual thresholding for cloud detection
    manual_threshold_value = 0.3 * np.max(nir_band)  # Adjust the threshold based on your data
    cloud_mask = nir_band > manual_threshold_value

    # Calculate cloud percentage
    total_pixels = cloud_mask.size
    cloud_pixels = np.sum(cloud_mask)
    cloud_coverage_percentage = (cloud_pixels / total_pixels) * 100
    print(f"Cloud coverage: {cloud_coverage_percentage:.2f}%")

    # Save the cloud mask as a GeoTIFF
    with rasterio.open(
            output_tiff_path, 'w',
            driver='GTiff',
            height=cloud_mask.shape[0],
            width=cloud_mask.shape[1],
            count=1, dtype=rasterio.uint8
    ) as dst:
        dst.write(cloud_mask.astype(np.uint8), 1)
    print(f"Cloud mask saved to: {output_tiff_path}")

    # Convert the cloud mask to JPEG format
    cloud_mask_normalized = (cloud_mask * 255).astype(np.uint8)  # Normalize mask to [0, 255]
    img = Image.fromarray(cloud_mask_normalized)
    img.save(output_jpeg_path, 'JPEG')
    print(f"Cloud mask JPEG saved to: {output_jpeg_path}")

    return cloud_coverage_percentage

with open(csv_file_path, mode='w', newline='') as csv_file:
    fieldnames = ['filename', 'cloud_coverage_percentage']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    # Loop through all .tif files in the input directory
    for filename in os.listdir(images_dir):
        if filename.endswith('.tif'):
            file_path = os.path.join(images_dir, filename)
            cloud_output_tiff_file = os.path.join(cloud_dir, f'cloud_{filename}')
            cloud_output_jpeg_file = os.path.join(cloud_dir, f'cloud_{filename.split(".")[0]}.jpeg')
            
            cloud_coverage_percentage = generate_and_save_cloud_mask(file_path, cloud_output_tiff_file, cloud_output_jpeg_file)
            
            writer.writerow({'filename': filename, 'cloud_coverage_percentage': cloud_coverage_percentage})

            print(f"Cloud coverage for {filename}: {cloud_coverage_percentage:.2f}% written to CSV")
