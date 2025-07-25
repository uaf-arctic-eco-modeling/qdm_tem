### Author: Hélène Genet, hgenet@alaska.edu 
### Institution: Arctic Eco Modeling
### Team, Institute of Arctic Biology, University of Alaska Fairbanks 
### Date: September 23 2024 
### Description: 
### Command: $ 


#import requests
#import zipfile
import pandas as pd
import xarray as xr
import numpy as np
from pyproj import Transformer

import argparse

parser = argparse.ArgumentParser(description='Argument description')
parser.add_argument('mask_path', type=str,help='path to the mask of the sub-region to be examined')
args = parser.parse_args()

### LOOP THROUGH THE DOWNSCALED TILES

## Function to transform pixel coordinates from EASE GRID 2.0 NORTH to WGS 1984
def trsf(row):
    transformer = Transformer.from_crs("EPSG:6931", "EPSG:4326")
    fx, fy = transformer.transform(row['X'], row['Y'])
    return fx, fy


dd = xr.open_dataset(args.mask_path)
#dd = xr.open_dataset('/Volumes/5TIV/PROCESSED/TILES/H01_V05/run-mask.nc')
dd = dd.to_dataframe()
dd.reset_index(inplace=True)
# Transform coordinates to compute length of day in TEM
coords = dd[['X','Y']].drop_duplicates()
coords[['lat','lon']] = pd.DataFrame(coords.apply(trsf, axis=1).tolist(), index= coords.index)
dd = dd[['X','Y','run']]
dd.loc[dd.run != 1.0, 'run'] = 0
dd['run'] = dd['run'].astype(int) 
# Convert back to netcdf file
dd = dd.sort_values(by=['Y','X'])
coords = coords.sort_values(by=['Y','X'])
nc1 = dd.set_index(['Y', 'X']).to_xarray()
nc2 = coords.set_index(['Y', 'X']).to_xarray()
nc = xr.merge([nc1, nc2])
nc['lat'] = nc['lat'].astype(np.single)
nc['lon'] = nc['lon'].astype(np.single)
nc['X'] = nc['X'].astype(np.single)
nc['Y'] = nc['Y'].astype(np.single)
nc['run'] = nc['run'].astype(np.intc)
nc['lat'].attrs={'standard_name':'latitude','units':'degree_north','_FillValue': 1.e+20}
nc['lon'].attrs={'standard_name':'longitude','units':'degree_east','_FillValue': 1.e+20}
nc['Y'].attrs={'standard_name':'projection_y_coordinate','long_name':'y coordinate of projection','units':'m','_FillValue': 1.e+20}
nc['X'].attrs={'standard_name':'projection_x_coordinate','long_name':'x coordinate of projection','units':'m','_FillValue': 1.e+20}
nc['run'].attrs={'standard_name':'mask','units':'','grid_mapping':'albers_conical_equal_area','_FillValue': -9999}
nc.to_netcdf(args.mask_path)


