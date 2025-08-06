### Author: Helene Genet, hgenet@alaska.edu
### Description: This short script lists the tiles overlaping a region of interest (Alaska in this example)

from osgeo import ogr, osr, gdal
import geopandas

# Read in the tile shapefile
tilemap = geopandas.read_file("/Volumes/5TIV/PROCESSED/TILEMAP2_0/tilemap.shp")

# Compute tile active area
tilemap["area_tile"] = tilemap.area / 10e6 # area in km2

# Read in the shapefile for the region of interest
region = geopandas.read_file("/Volumes/BACKUP2018/DATA/AK/State_3338.shp")

# Change projection if needed
if tilemap.crs != region.crs:
  region = region.to_crs(tilemap.crs)

# Clip original tiles map
cliptiles = tilemap.clip(region)
cliptiles["area_clip"] = cliptiles.area / 10e6 # area in km2

# Compute tile area overlaping the area of interest
tile_list = cliptiles.groupby(['tile']).sum(['area_tile','area_clip'])
tile_list.rename(columns={'DN': 'num_polygon'}, inplace=True)
tile_list = tile_list.drop('Processed', axis=1) 
tile_list = tile_list.reset_index()


# Write out the clipped shapefile and the csv of the 
cliptiles.to_file("/Users/helenegenet/Helene/TEM/INPUT/production/site_region_extract/AK_tile.shp")
tile_list.to_csv("/Users/helenegenet/Helene/TEM/INPUT/production/site_region_extract/AK_tile.csv")
