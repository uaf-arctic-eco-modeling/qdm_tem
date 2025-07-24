import geopandas as gp
import numpy as np
import os
import pandas as pd
import rasterio
from rasterio import features
from affine import Affine

cntrypath = os.getenv('cntrypath')
cntryrst = os.getenv('cntryrst')
staterst = os.getenv('staterst')
ecoregpath = os.getenv('ecoregpath')
ecorgrst = os.getenv('ecorgrst')
biomerst = os.getenv('biomerst')
ecobiomerst = os.getenv('ecobiomerst')
realmrst = os.getenv('realmrst')
lcpath = os.getenv('lcpath')
classpath = os.getenv('classpath')
drainpth = os.getenv('drainpth')
mskpath = os.getenv('mskpath')
subregrst = os.getenv('subregrst')
cmtrst = os.getenv('cmtrst')
missval = os.getenv('missval')
extent = os.getenv('extent').replace(" ", ",").split(',')
res = os.getenv('resolution').replace(" ", ",").split(',')


### Read in the original shapefiles
glob = gp.read_file(cntrypath)
eco = gp.read_file(ecoregpath)


### Indexing countries and ecoregions
cntrydf = pd.DataFrame(glob.shapeGroup.unique())
cntrydf.reset_index(inplace=True)
cntrydf = cntrydf.set_axis(['ctry_idx','shapeGroup'], axis=1)
cntrydf['ctry_idx'] += 1
cntrydff  = glob.merge(cntrydf, on='shapeGroup', how='left')
cntrygdf = gp.GeoDataFrame(cntrydff)

statedf = pd.DataFrame(glob.shapeName.unique())
statedf.reset_index(inplace=True)
statedf = statedf.set_axis(['state_idx','shapeName'], axis=1)
statedf['state_idx'] += 1
statedff  = glob.merge(statedf, on='shapeName', how='left')
stategdf = gp.GeoDataFrame(statedff)

ecorgdf = pd.DataFrame(eco.ECO_NAME.unique())
ecorgdf.reset_index(inplace=True)
ecorgdf = ecorgdf.set_axis(['ecoreg_idx','ECO_NAME'], axis=1)
ecorgdf['ecoreg_idx'] += 1
ecorgdff  = eco.merge(ecorgdf, on='ECO_NAME', how='left')
ecorggdf = gp.GeoDataFrame(ecorgdff)

biomedf = pd.DataFrame(eco.BIOME_NAME.unique())
biomedf.reset_index(inplace=True)
biomedf = biomedf.set_axis(['biome_idx','BIOME_NAME'], axis=1)
biomedf['biome_idx'] += 1
biomedff  = eco.merge(biomedf, on='BIOME_NAME', how='left')
biomegdf = gp.GeoDataFrame(biomedff)

ecobiomedf = pd.DataFrame(eco.ECO_BIOME_.unique())
ecobiomedf.reset_index(inplace=True)
ecobiomedf = ecobiomedf.set_axis(['ecobiome_idx','ECO_BIOME_'], axis=1)
ecobiomedf['ecobiome_idx'] += 1
ecobiomedff  = eco.merge(ecobiomedf, on='ECO_BIOME_', how='left')
ecobiomegdf = gp.GeoDataFrame(ecobiomedff)

realmdf = pd.DataFrame(eco.REALM.unique())
realmdf.reset_index(inplace=True)
realmdf = realmdf.set_axis(['realm_idx','REALM'], axis=1)
realmdf['realm_idx'] += 1
realmdff  = eco.merge(realmdf, on='REALM', how='left')
realmgdf = gp.GeoDataFrame(realmdff)



### Get spatial information from the mask
rst = rasterio.open(mskpath)
meta = rst.meta.copy()
meta.update(compress='lzw')



### Rasterize the indices
with rasterio.open(cntryrst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(cntrygdf.geometry, cntrygdf.ctry_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

with rasterio.open(staterst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(stategdf.geometry, stategdf.state_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

with rasterio.open(ecorgrst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(ecorggdf.geometry, ecorggdf.ecoreg_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

with rasterio.open(biomerst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(biomegdf.geometry, biomegdf.biome_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

with rasterio.open(ecobiomerst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(ecobiomegdf.geometry, ecobiomegdf.ecobiome_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)

with rasterio.open(realmrst, 'w+', **meta) as out:
    out_arr = out.read(1)
    shapes = ((geom,value) for geom, value in zip(realmgdf.geometry, realmgdf.realm_idx))
    burned = features.rasterize(shapes=shapes, fill=-9999, out=out_arr, transform=out.transform)
    out.write_band(1, burned)



### Overlap all rasters to get the identification

c1 = rasterio.open(cntryrst)
b1 = c1.read(1)
b11d = pd.DataFrame(b1.flatten())
b11d = b11d.set_axis(['ctry_idx'], axis=1)

c2 = rasterio.open(staterst)
b2 = c2.read(1)
b21d = pd.DataFrame(b2.flatten())
b21d = b21d.set_axis(['state_idx'], axis=1)

c3 = rasterio.open(ecorgrst)
b3 = c3.read(1)
b31d = pd.DataFrame(b3.flatten())
b31d = b31d.set_axis(['ecoreg_idx'], axis=1)

c4 = rasterio.open(biomerst)
b4 = c4.read(1)
b41d = pd.DataFrame(b4.flatten())
b41d = b41d.set_axis(['biome_idx'], axis=1)

c5 = rasterio.open(ecobiomerst)
b5 = c5.read(1)
b51d = pd.DataFrame(b5.flatten())
b51d = b51d.set_axis(['ecobiome_idx'], axis=1)

c6 = rasterio.open(realmrst)
b6 = c6.read(1)
b61d = pd.DataFrame(b6.flatten())
b61d = b61d.set_axis(['realm_idx'], axis=1)

c7 = rasterio.open(lcpath)
b7 = c7.read(1)
b71d = pd.DataFrame(b7.flatten())
b71d = b71d.set_axis(['lc_idx'], axis=1)

c8 = rasterio.open(drainpth)
b8 = c8.read(1)
b81d = pd.DataFrame(b8.flatten())
b81d = b81d.set_axis(['drain_idx'], axis=1)

draindf = pd.DataFrame(np.unique(b8))
draindf = draindf.set_axis(['drain_idx'], axis=1)
draindf['drain_name'] = np.where(draindf['drain_idx'] == 1.0 , 'poorly', 'well')
#draindf['drain_idx'] += 1
#draindf['drain_name'] = np.where(draindf['drain_idx'] == 1.0 , 'well', np.where(draindf['drain_idx'] == 2.0 , 'poorly', 'N/A'))

c9 = rasterio.open(mskpath)
b9 = c9.read(1)
b91d = pd.DataFrame(b9.flatten())
b91d = b91d.set_axis(['mask_idx'], axis=1)



### Create the ecotype ID and store them in a table

ecotype = pd.concat([b11d, b21d, b31d, b41d, b51d, b61d, b71d, b81d, b91d], axis = 1)
#ecotype['ecotype'] = ecotype['lc_idx'].astype(int).apply(lambda x: '{0:0>3}'.format(x)) + ecotype['drain_idx'].astype(int).apply(lambda x: '{0:0>3}'.format(x)) + ecotype['ecoreg_idx'].astype(int).apply(lambda x: '{0:0>3}'.format(x)) + ecotype['ctry_idx'].astype(int).apply(lambda x: '{0:0>3}'.format(x)) + ecotype['biome_idx'].astype(int).apply(lambda x: '{0:0>3}'.format(x)) 
#ecotype['ecotype'] = np.where(ecotype['mask_idx'] == 0 , '000000000000000', ecotype['ecotype'])
## Add categories names
classif = pd.read_csv(classpath)  
classif = classif.rename(columns={"value": "lc_idx"})
ecotype = pd.merge(ecotype, classif.drop(['groupname'], axis=1), how="left", on=["lc_idx"])
ecotype = pd.merge(ecotype, ecorgdf, how="left", on=["ecoreg_idx"])
ecotype = pd.merge(ecotype, biomedf, how="left", on=["biome_idx"])
ecotype = pd.merge(ecotype, ecobiomedf, how="left", on=["ecobiome_idx"])
ecotype = pd.merge(ecotype, realmdf, how="left", on=["realm_idx"])
ecotype['REALM'] = np.where(ecotype['REALM'] == 'N/A', 'Nearctic',ecotype['REALM'])
ecotype = pd.merge(ecotype, cntrydf, how="left", on=["ctry_idx"])
ecotype = pd.merge(ecotype, statedf, how="left", on=["state_idx"])
# drainage class 0: well-drained; 1: poorly-drained
ecotype = pd.merge(ecotype, draindf, how="left", on=["drain_idx"])
# define subregion
ecotype['subreg'] = np.where((ecotype['shapeName'] == 'Alaska') | 
		(ecotype['ECO_NAME'] == 'Pacific Coastal Mountain icefields and tundra') | 
		(ecotype['ECO_NAME'] == 'Alaska-St. Elias Range tundra') | 
		(ecotype['ECO_NAME'] == 'Interior Yukon-Alaska alpine tundra') | 
		(ecotype['ECO_NAME'] == 'Brooks-British Range tundra') | 
		(ecotype['ECO_NAME'] == 'Arctic foothills tundra') | 
		(ecotype['ECO_NAME'] == 'Interior Yukon-Alaska alpine tundra'), 'Western North America',
			np.where((ecotype['shapeGroup'] == 'CAN') | (ecotype['shapeGroup'] == 'GRL'), 
				np.where((ecotype['shapeName'] == 'Quebec') | 
					(ecotype['shapeName'] == 'Ontario') |
					(ecotype['shapeName'] == 'Newfoundland and Labrador') |
					(ecotype['ECO_NAME'] == 'Southern Hudson Bay taiga') |
					(ecotype['ECO_NAME'] == 'Central Canadian Shield forests') |
					(ecotype['ECO_NAME'] == 'Eastern Canadian Forest-Boreal transition') |
					(ecotype['shapeGroup'] == 'GRL'), 'Eastern North America', 'Central North America'),
					np.where((ecotype['shapeGroup'] == 'NOR') |
						(ecotype['shapeGroup'] == 'SWE') |
						(ecotype['shapeGroup'] == 'FIN') |
						(ecotype['shapeGroup'] == 'ISL') |
						(ecotype['ECO_NAME'] == 'Kola Peninsula tundra') |
						(ecotype['ECO_NAME'] == 'Scandinavian and Russian taiga') |
						(ecotype['ECO_NAME'] == 'Temperate Broadleaf & Mixed Forests') |
						(ecotype['ECO_NAME'] == 'Urals montane forest and taiga'), 'Western Eurasia',
						np.where((ecotype['ECO_NAME'] == 'Yamal-Gydan tundra') |
							(ecotype['ECO_NAME'] == 'Russian Arctic desert') |
							(ecotype['ECO_NAME'] == 'West Siberian taiga') |
							(ecotype['ECO_NAME'] == 'Western Siberian hemiboreal forests') |
							(ecotype['ECO_NAME'] == 'South Siberian forest steppe') |
							(ecotype['ECO_NAME'] == 'Northwest Russian-Novaya Zemlya tundra') |
							(ecotype['ECO_NAME'] == 'Trans-Baikal conifer forests') |
							(ecotype['ECO_NAME'] == 'Kazakh forest steppe'), 'Central Eurasia', 
							np.where((ecotype['shapeGroup'] == 'RUS'), 'Eastern Eurasia', 'N/A')))))

ecotype['subreg'] = np.where((ecotype['ECO_NAME'] == 'Ogilvie-MacKenzie alpine tundra'),'Central North America',ecotype['subreg'])

subregdf = pd.DataFrame(ecotype['subreg'].unique())
subregdf.reset_index(inplace=True)
subregdf = subregdf.set_axis(['subreg_idx','subreg'], axis=1)
subregdf['subreg_idx'] += 1
ecotype = pd.merge(ecotype, subregdf, how="left", on=["subreg"])
subreg = np.reshape(ecotype['subreg_idx'], (-1, rasterio.open(lcpath).read(1).shape[1]))

with rasterio.open(subregrst, 
                  mode="w+", 
                  **meta,) as out:
    out.write(subreg, 1)



# identify alpine areas
ecotype['alpine'] = np.where(ecotype['ECO_NAME'].str.contains('mountain', case=False),'alpine',
	np.where(ecotype['ECO_NAME'].str.contains('mountains', case=False),'alpine',
		np.where(ecotype['ECO_NAME'].str.contains('alpine', case=False),'alpine',
			np.where(ecotype['ECO_NAME'].str.contains('range', case=False),'alpine',
				np.where(ecotype['ECO_NAME'].str.contains('rockies', case=False),'alpine',
					np.where(ecotype['ECO_NAME'].str.contains('cordillera', case=False),'alpine',
						np.where(ecotype['ECO_NAME'].str.contains('rock', case=False),'alpine','NaN')))))))
ecotype['alpine_idx'] = np.where(ecotype['alpine'] == 'alpine', 1, 0)


# crosswalk land cover with community parameterizations
ecotype['community'] = np.where((ecotype['classname '] == 'White Spruce forest'), 'white spruce forest',
	np.where((ecotype['classname '] == 'Black Spruce forest') | 
		(ecotype['classname '] == 'Spruce forest') | 
		(ecotype['classname '] == 'Fir forest') | 
		(ecotype['classname '] == 'Hemlock forest'), 'black spruce forest',
		np.where((ecotype['classname '] == 'Aspen forest'), 'aspen forest',
			np.where((ecotype['classname '] == 'Birch forest') | 
				(ecotype['classname '] == 'Poplar forest') | 
				(ecotype['classname '] == 'Maple') | 
				(ecotype['classname '] == 'Oak forest') | 
				(ecotype['classname '] == 'Linden'), 'birch forest',
				np.where((ecotype['classname '] == 'Mixed forest'), 'mixed forest',
					np.where((ecotype['classname '] == 'Larch forest'), 'larch forest',
						np.where((ecotype['classname '] == 'Scotts Pine forest') | 
							(ecotype['classname '] == 'Siberian Pine'), 'scots pine forest',
							np.where((ecotype['classname '] == 'Jack Pine forest'), 'jack pine forest',
								np.where((ecotype['classname '] == 'Herbaceous') | 
									(ecotype['classname '] == 'Graminoid tundra'), 'tussock tundra',
									np.where((ecotype['classname '] == 'Other shrublands') | 
										(ecotype['classname '] == 'Cedar Elfin Wood') | 
										(ecotype['classname '] == 'Erect-shrub tundra') | 
										(ecotype['classname '] == 'Shrub tundra') | 
										(ecotype['classname '] == 'Alpine shrubland') | 
										(ecotype['classname '] == 'Prostrate-shrub tundra') | 
										(ecotype['classname '] == 'Riparian shrubland'), 'shrub tundra',
										np.where((ecotype['classname '] == 'Barren tundra') | 
											(ecotype['classname '] == 'Sparsely Vegetated'), 'heath tundra',
											np.where((ecotype['classname '] == 'Fen'), 'fen',
												np.where((ecotype['classname '] == 'Bog'), 'bog',
													np.where((ecotype['classname '] == 'Wet-sedge tundra') | 
														(ecotype['classname '] == 'Marsh'), 'wetsedge tundra','N/A'))))))))))))))
ecotype['community'] = np.where((ecotype['classname '] == 'Pine forest'), 'jack pine forest',ecotype['community'])
ecotype['community'] = np.where((ecotype['classname '] == 'Pine forest') & (ecotype['REALM'] == 'Palearctic'), 'scots pine forest',ecotype['community'])

					
# remove all the variable values outside the mask
ecotype['classname '] = np.where((ecotype['mask_idx'] == 0),'',ecotype['classname '])
ecotype['ECO_NAME'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['ECO_NAME'])
ecotype['BIOME_NAME'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['BIOME_NAME'])
ecotype['shapeGroup'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['shapeGroup'])
ecotype['drain_name'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['drain_name'])
ecotype['subreg'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['subreg'])
ecotype['community'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['community'])
ecotype['alpine'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['alpine'])
ecotype['REALM'] = np.where((ecotype['mask_idx'] == 0),'',ecotype['REALM'])


### Crosswalk
## General classes
ecotype['CMT'] = 'CMT00'
ecotype['CMT'] = np.where((ecotype['community'] == 'black spruce forest'),'CMT01',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'white spruce forest'),'CMT02',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'jack pine forest'),'CMT66',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'scots pine forest'),'CMT74',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'larch forest'),'CMT71',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'mixed forest'),'CMT67',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'birch forest'),'CMT03',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'aspen forest'),'CMT65',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra'),'CMT04',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'tussock tundra'),'CMT05',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'heath tundra'),'CMT07',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'wetsedge tundra'),'CMT06',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'bog'),'CMT31',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'fen'),'CMT55',ecotype['CMT'])

## General classes simplification
#ecotype['CMT'] = 'CMT00'
#ecotype['CMT'] = np.where((ecotype['community'] == 'black spruce forest'),'CMT01',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'white spruce forest'),'CMT02',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'jack pine forest'),'CMT01',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'scots pine forest'),'CMT01',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'larch forest'),'CMT03',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'mixed forest'),'CMT03',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'birch forest'),'CMT03',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'aspen forest'),'CMT03',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra'),'CMT04',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'tussock tundra'),'CMT05',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'heath tundra'),'CMT07',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'wetsedge tundra'),'CMT06',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'bog'),'CMT31',ecotype['CMT'])
#ecotype['CMT'] = np.where((ecotype['community'] == 'fen'),'CMT31',ecotype['CMT'])

## Refinment
ecotype['CMT'] = np.where((ecotype['community'] == 'black spruce forest') & (ecotype['subreg'] == 'Western North America') & (ecotype['drain_name'] == 'poorly'), 'CMT13', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'black spruce forest') & ((ecotype['subreg'] == 'Central North America') | (ecotype['subreg'] == 'Eastern North America')) & (ecotype['drain_name'] == 'poorly'), 'CMT60', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'black spruce forest') & ((ecotype['subreg'] == 'Central North America') | (ecotype['subreg'] == 'Eastern North America')) & (ecotype['drain_name'] == 'well'), 'CMT69', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'bog') & ((ecotype['subreg'] == 'Central North America') | (ecotype['subreg'] == 'Eastern North America')), 'CMT61', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'bog') & ((ecotype['subreg'] == 'Eastern Eurasia') | (ecotype['subreg'] == 'Central Eurasia')), 'CMT75', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'bog') & (ecotype['subreg'] == 'Western Eurasia'), 'CMT80', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'bog') & ((ecotype['ECO_NAME'] == 'Russian Arctic desert') | (ecotype['ECO_NAME'] == 'Kola Peninsula tundra') | (ecotype['ECO_NAME'] == 'Scandinavian coastal conifer forests') | (ecotype['ECO_NAME'] == 'Scandinavian Montane Birch forest and grasslands')) , 'CMT92', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'fen') & (ecotype['REALM'] == 'Palearctic') , 'CMT91', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'heath tundra') & (ecotype['subreg'] == 'Central North America'), 'CMT52', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'heath tundra') & (ecotype['subreg'] == 'Eastern North America'), 'CMT90', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'heath tundra') & (ecotype['REALM'] == 'Palearctic'), 'CMT90', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'larch forest') & ((ecotype['subreg'] == 'Central Eurasia') | (ecotype['subreg'] == 'Western Eurasia')),'CMT72',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'mixed forest') & (ecotype['REALM'] == 'Palearctic'),'CMT77',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'scots pine forest') & (ecotype['subreg'] == 'Western Eurasia'),'CMT82',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra') & ((ecotype['subreg'] == 'Central North America') | (ecotype['subreg'] == 'Eastern North America')), 'CMT50', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra') & (ecotype['subreg'] == 'Eastern Eurasia'), 'CMT70', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra') & ((ecotype['subreg'] == 'Western Eurasia') | (ecotype['subreg'] == 'Central Eurasia')), 'CMT76', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'shrub tundra') & (ecotype['alpine'] == 'alpine'),'CMT20',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'tussock tundra') & ((ecotype['subreg'] == 'Central North America') | (ecotype['subreg'] == 'Eastern North America')), 'CMT51', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'tussock tundra') & (ecotype['REALM'] == 'Palearctic'), 'CMT73', ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'tussock tundra') & (ecotype['alpine'] == 'alpine'),'CMT21',ecotype['CMT'])
ecotype['CMT'] = np.where((ecotype['community'] == 'wetsedge tundra') & (ecotype['REALM'] == 'Palearctic'), 'CMT77', ecotype['CMT'])

ecotype['CMT'] = np.where((ecotype['mask_idx'] == 0),missval,ecotype['CMT'])

## Verification
# Check that all pixels with LC class have a CMT
freq = pd.DataFrame(ecotype.value_counts(['community','CMT']))
freq.reset_index(inplace=True)
freq = freq.sort_values(by=['community'], ascending=[True])
freq
freq.to_csv('/Volumes/5TIV/PROCESSED/VEGETATION/verification_classification.csv', index=False)
# Check crosswalk
freq = pd.DataFrame(ecotype.value_counts(['community', 'classname ']))
freq.reset_index(inplace=True)
freq = freq.sort_values(by=['community'], ascending=[True])
freq
freq.to_csv('/Volumes/5TIV/PROCESSED/VEGETATION/verification_crosswalk.csv', index=False)
# Check classification rules
freq = pd.DataFrame(ecotype.value_counts(['community', 'REALM','subreg','drain_name','alpine','CMT']))
freq.reset_index(inplace=True)
freq = freq.sort_values(by=['community', 'REALM','subreg','drain_name','alpine','CMT'], ascending=[True,True,True,True,True,True])
freq
freq.to_csv('/Volumes/5TIV/PROCESSED/VEGETATION/verification_community.csv', index=False)


### Exporting

ecotype = pd.merge(ecotype, subregdf, how="left", on=["subreg"])
ecotype['CMT_num'] =pd.to_numeric(ecotype['CMT'].str.extract('(\d+)', expand=False)).fillna(missval).astype(int)
ecotype['CMT_num'] = np.where((ecotype['mask_idx'] == 0),missval,ecotype['CMT_num'])

cmt = np.reshape(ecotype['CMT_num'], (-1, rasterio.open(lcpath).read(1).shape[1]))

with rasterio.open(cmtrst, mode="w+", **meta,) as out:
    out.write(cmt, 1)




