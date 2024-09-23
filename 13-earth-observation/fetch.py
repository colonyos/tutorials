import numpy as np
import openeo
import time
import rasterio
import os
from pathlib import Path
from matplotlib import pyplot as plt

eo_service_url = os.getenv('OPENEO_URL')
user = os.getenv('OPENEO_USER')
passwd = os.getenv('OPENEO_PASSWORD')
connection = openeo.connect(eo_service_url)

print(eo_service_url)
print(user)
print(connection.authenticate_basic(username=user, password=passwd))

aoi = {
    'east': 22.136334940987638,  # max longitude
    'south': 65.63560585326866,  # min latitude
    'west': 21.79257719972466,   # min longitude
    'north': 65.78212032521256   # max latitude
}

def poll_job(job, polling_interval=10):
    while True:
        status = job.status()
        print(f"Job status: {status}")
        if status == "finished":
            print("Job has finished.")
            break
        time.sleep(polling_interval)

def convert_gtiff_to_img(file_path: str, output_png_path: str, title: str=""):
    with rasterio.open(file_path) as im:
        r = im.read(1)
        g = im.read(2)
        b = im.read(3)

        r_normalized = normalize(r)
        g_normalized = normalize(g)
        b_normalized = normalize(b)

        rgb = np.dstack((r_normalized, g_normalized, b_normalized))

    plt.imsave(output_png_path, rgb)

def normalize(array):
    array_min, array_max = np.percentile(array, (1, 99))
    array = np.clip(array, array_min, array_max)
    return ((array - array_min) / (array_max - array_min) * 255).astype(np.uint8)

class Dict2Class(object):
    def __init__(self, my_dict):

        for key in my_dict:
            if type(my_dict[key]) is dict:
                if key in ["bbox", "timespans", "polygons"]:
                    my_dict[key] = Dict2Class(my_dict[key])
            setattr(self, key, my_dict[key])

s2 = {
    "s2_msi_l2a": "s2_msi_l2a",
    "bbox": {
    }
}
s2 = Dict2Class(s2)

cube = connection.load_collection(collection_id=s2.s2_msi_l2a,
                         spatial_extent=aoi,
                         temporal_extent=["2024-08-02T00:00:00Z", "2024-08-10T10:00:00Z"],
                         bands=['b04', 'b03', 'b02', 'b08'],
                        )

job = cube.create_job(out_format="gtiff",
    title= "Max time demo job1",
    description = "This job was created from ColonyOS")

print("Creating OpenEO job, ID=", job.job_id)
print("Starting OpenEO job, ID=", job.job_id)
print("Waiting ...")
job.start_and_wait()
poll_job(job)

results = job.get_results()
results.get_metadata()
results.download_files("data/out")

directory = Path('data/out')

print("Cleaning junk files ...")
for file in directory.iterdir():
    if file.is_file() and file.suffix != '.tif':
        file.unlink()
        print(f"Deleted: {file}")

print("Deletion complete.")

print("Converting GeoTiff to JPEG ...")
def convert_all_tif_to_jpg(directory: str):
    dir_path = Path(directory)
    
    for tif_file in dir_path.glob('*.tif'):
        jpg_file = tif_file.with_suffix('.jpg')
        convert_gtiff_to_img(str(tif_file), str(jpg_file))
        print(f"Converted {tif_file} to {jpg_file}")

convert_all_tif_to_jpg('data/out')
