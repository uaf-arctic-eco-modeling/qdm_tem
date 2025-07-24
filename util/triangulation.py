import subprocess
import os
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

tilemap = '/Volumes/5TIV/PROCESSED/TILEMAP2_0/tilemap.shp'
indir = '/Volumes/5TIV/PROCESSED/TILES2_0'
siteoutdir = '/Users/helenegenet/Helene/TEM/INPUT/production/site_extract'


site = 'bnz-bog' 
site_lat = 64.6955
site_lon = -148.3208
coords = [site_lon, site_lat]


#### FIND THE TILE IN WHICH THE SITE IS LOCATED IN

### Read in the tile shapefile
gdf1 = gpd.read_file(tilemap)

### Read and transform the site coordinates
sitepoint = pd.DataFrame(np.array([[site, float(site_lon), float(site_lat)]]), columns=['sitename','lon','lat'])
geometry = [Point(xy) for xy in zip(sitepoint['lon'], sitepoint['lat'])]
gdf2 = gpd.GeoDataFrame(sitepoint, geometry=geometry)
gdf2.set_crs("EPSG:4326", inplace=True)
gdf2 = gdf2.to_crs(gdf1.crs)

### Select the tile overlaping the site
tilename = gdf1.iloc[gdf1.distance(gdf2.geometry.iloc[0]).idxmin()]['tile']
tilename


#### FIND THE PIXEL OVERLAYING THE SITE

### Create a directory for site inputs
if not os.path.exists(os.path.join(siteoutdir,site)):
  os.makedirs(os.path.join(siteoutdir,site))

for fn in os.listdir(os.path.join(indir,tilename,'input')):
  print(fn)
  ds = xr.open_dataset(os.path.join(indir,tilename,'input',fn))
  if 'X' in list(ds.coords.keys()):
    subprocess.run("ncks -O -h -d Y," + str(gdf2.geometry[0].y) + " -d X," + str(gdf2.geometry[0].x) + " " + os.path.join(indir,tilename,'input',fn) + " " + os.path.join(siteoutdir,site,fn), shell=True, capture_output=True, text=True)
  else:
    subprocess.run("cp " + os.path.join(indir,tilename,'input',fn) + " " + os.path.join(siteoutdir,site,fn), shell=True, capture_output=True, text=True)

