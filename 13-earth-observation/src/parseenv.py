import os
import json

aoi_str = os.getenv("aoi")
aoi = json.loads(aoi_str)
temporal_extent = os.getenv("temporal_extent")
bands = os.getenv("bands")
label = os.getenv("label")
eo_service_url = os.getenv("openeourl")
user = os.getenv("openeouser")
passwd = os.getenv("openeopasswd")

print(aoi)
print(temporal_extent)
print(bands)
print(label)
print(eo_service_url)
print(user)
print(passwd)

