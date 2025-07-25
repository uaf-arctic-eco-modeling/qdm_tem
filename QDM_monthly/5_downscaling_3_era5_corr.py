import os
import xarray as xr
import pandas as pd
import numpy as np
import gc


### Import information from shell
out_path = os.getenv('outdir')
mask_path = os.getenv('mask')
wc_path = os.getenv('wc')
era5_path = os.getenv('era5')
cj_path = os.getenv('cj')
terra_path = os.getenv('terra')
cmip_path = os.getenv('cmipoutdir')
sclist = os.getenv('sclist').split(',')
sclist_short = os.getenv('sclist_short').split(',')
modlist = os.getenv('modlist').split(',')
cmipversion = os.getenv('cmipversion')
topo_path = os.getenv('topo')




### READ DATA

## Era5
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/ERA5','era5_gf.nc'))
era5 = ddo.to_dataframe()
era5.reset_index(inplace=True)

## Worldclim
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/WORLD_CLIM','wc_unit.nc'))
wc = ddo.to_dataframe()
wc.reset_index(inplace=True)



### BIAS CORRECTION
era5['year'] = era5['time'].dt.year
era5['month'] = era5['time'].dt.month
era5m = era5[(era5['year'] > 1969) & (era5['year'] < 2001)].groupby(['month','lat','lon'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].mean()
era5m.reset_index(inplace=True)
era5m.rename(columns={'tas_oc': 'tas_oc_era5', 'precip_mm': 'precip_mm_era5', 'srad_wm2':'srad_wm2_era5','vapo_kpa':'vapo_kpa_era5'}, inplace=True)

corr = pd.merge(era5m,wc[['lat','lon','month','tas_oc','precip_mm','srad_wm2','vapo_kpa']],how='outer',on=['lat','lon','month'])
corr['tas_oc_corr'] = corr['tas_oc_era5'] - corr['tas_oc']
corr['precip_mm_corr'] = np.where(corr['precip_mm'] == 0, 1, corr['precip_mm_era5'] / corr['precip_mm'])
corr['srad_wm2_corr'] = np.where(corr['srad_wm2'] == 0, 1, corr['srad_wm2_era5'] / corr['srad_wm2'])
corr['vapo_kpa_corr'] = np.where(corr['vapo_kpa'] == 0, 1, corr['vapo_kpa_era5'] / corr['vapo_kpa'])

## Force corrected values to zero instead of NaN when correction factor is zero
era5c = pd.merge(era5,corr[['lat','lon','month','tas_oc_corr','precip_mm_corr','srad_wm2_corr','vapo_kpa_corr']],how='outer',on=['lat','lon','month'])
era5c['tas_oc_c'] = np.where(era5c['tas_oc_corr'] == 0, 0, era5c['tas_oc'] - era5c['tas_oc_corr'])
era5c['precip_mm_c'] = np.where(era5c['precip_mm_corr'] == 0, 0, era5c['precip_mm'] / era5c['precip_mm_corr'])
era5c['srad_wm2_c'] = np.where(era5c['srad_wm2_corr'] == 0, 0, era5c['srad_wm2'] / era5c['srad_wm2_corr'])
era5c['vapo_kpa_c'] = np.where(era5c['vapo_kpa_corr'] == 0, 0, era5c['vapo_kpa'] / era5c['vapo_kpa_corr'])

del [corr]
gc.collect()


## Check for errors
if era5c[era5c['srad_wm2_c'] < 0].shape[0] > 0:
    print('Negative radiation values!')
    if era5c[era5c['srad_wm2_c']<0]['srad_wm2_c'].min() < -0.5:
        print('NEGATIVE VALUES OF RADIATION < -0.5!')
        era5c['srad_wm2_c'] = np.where(era5c['srad_wm2_c'] < 0, 0, era5c['srad_wm2_c'])
    else:
        era5c['srad_wm2_c'] = np.where(era5c['srad_wm2_c'] < 0, 0, era5c['srad_wm2_c'])

if era5c[era5c['precip_mm_c'] < 0].shape[0] > 0:
    print('Negative precipitation values!')
    if era5c[era5c['precip_mm_c']<0]['precip_mm_c'].min() < -0.5:
        print('NEGATIVE VALUES OF PRECIPITATION < -0.5!')
        era5c['precip_mm_c'] = np.where(era5c['precip_mm_c'] < 0, 0, era5c['precip_mm_c'])
    else:
        era5c['precip_mm_c'] = np.where(era5c['precip_mm_c'] < 0, 0, era5c['precip_mm_c'])

if era5c[era5c['vapo_kpa_c'] < 0].shape[0] > 0:
    print('Negative pressure values!')
    if era5c[era5c['vapo_kpa_c']<0]['vapo_kpa_c'].min() < -0.1:
        print('NEGATIVE VALUES OF VAPOR PRESSURE < -0.1!')
        era5c['vapo_kpa_c'] = np.where(era5c['vapo_kpa_c'] < 0, 0, era5c['vapo_kpa_c'])
    else:
        era5c['vapo_kpa_c'] = np.where(era5c['vapo_kpa_c'] < 0, 0, era5c['vapo_kpa_c'])

if era5c[(era5c['tas_oc_c'] < -100) | (era5c['tas_oc_c'] > 50)].shape[0] > 0:
    print('Absolute temperature values too high!')
    era5c[(era5c['tas_oc_c'] < -100) | (era5c['tas_oc_c'] > 50)]

era5c = era5c[['lon', 'lat', 'time', 'tas_oc_c', 'precip_mm_c', 'srad_wm2_c', 'vapo_kpa_c']]
era5c.rename(columns={'tas_oc_c': 'tas_oc', 'vapo_kpa_c': 'vapo_kpa', 'precip_mm_c': 'precip_mm', 'srad_wm2_c':'srad_wm2'}, inplace=True)

era5nc = era5c.set_index(['time', 'lat', 'lon']).to_xarray()
era5nc.to_netcdf(os.path.join(out_path,'climate_downscaling/ERA5','era5_corr.nc'),unlimited_dims='time')
del [era5, era5c]
gc.collect()





