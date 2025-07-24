import os
import numpy as np
import rasterio
import sys
import argparse



maskpath = os.getenv('mskpath')
clay_org_path = os.getenv('clay_org_path')
clay_out_path = os.getenv('clay_out_path')
clay_coarse_path = os.getenv('clay_coarse_path')
silt_org_path = os.getenv('silt_org_path')
silt_out_path = os.getenv('silt_out_path')
silt_coarse_path = os.getenv('silt_coarse_path')
extent = os.getenv('extent').replace(" ", ",").split(',')
res = os.getenv('resolution').replace(" ", ",").split(',')


c1 = rasterio.open(clay_org_path)
b1 = c1.read(1)
c2 = rasterio.open(clay_coarse_path)
b2 = c2.read(1)
b4 = np.where((b1 == -9999) ,b2,b1)
with rasterio.open(clay_out_path, 'w', **c1.meta) as dst:
    dst.write(b4.astype(rasterio.int32), 1)

c1 = rasterio.open(silt_org_path)
b1 = c1.read(1)
c2 = rasterio.open(silt_coarse_path)
b2 = c2.read(1)
b4 = np.where((b1 == -9999) ,b2,b1)
with rasterio.open(silt_out_path, 'w', **c1.meta) as dst:
    dst.write(b4.astype(rasterio.int32), 1)

