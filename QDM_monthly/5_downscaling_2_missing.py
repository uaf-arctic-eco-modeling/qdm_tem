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



### CRU-JRA

## READ DATA
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CRU_JRA','cj_unit.nc'))
cj = ddo.to_dataframe()
cj.reset_index(inplace=True)


## CHECK FOR GAPS
cjcheck = cj.sort_values(['lat', 'lon','time'])
cjcheck['deltas'] = cjcheck['time'].diff()[1:].dt.days
cjcheck[cjcheck['deltas'] > 31].shape[0]
if cjcheck[cjcheck['deltas'] > 31].shape[0] > 0:
    print('CRU-JRA number of gaps: ' + cjcheck[cjcheck['deltas'] > 31].shape[0])
    ds = pd.date_range(start='1901-01-01', end='2023-12-01', freq='MS')
    lats = cj[['lat']].drop_duplicates()
    lons = cj[['lon']].drop_duplicates()
    da = xr.DataArray(np.arange(len(ds)*len(lats)*len(lons)).reshape(len(ds), len(lats), len(lons)), [("time", ds),("lat", lats['lat']), ("lon", lons['lon'])]).rename("my_data").to_dataframe()
    da.reset_index(inplace=True)
    cj = pd.merge(cj,da,how='outer',on=['time','lat','lon'])


## CHECK FOR MISSING VALUES 
cjmean = cj.dropna().groupby(['lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].mean()
cjmean.reset_index(inplace=True)
cjmean.rename(columns={'tas_oc': 'tas_oc_avg', 'vapo_kpa': 'vapo_kpa_avg', 'precip_mm': 'precip_mm_avg', 'srad_wm2':'srad_wm2_avg'}, inplace=True)
cj = pd.merge(cj, cjmean, how='outer', on=['lat','lon','month'])
if (len(cj[np.isnan(cj['tas_oc'])]) > 0)| (len(cj[np.isnan(cj['precip_mm'])]) > 0) | (len(cj[np.isnan(cj['srad_wm2'])]) > 0) | (len(cj[np.isnan(cj['vapo_kpa'])]) > 0):
    cj.loc[np.isnan(cj.tas_oc), 'tas_oc'] = cj.tas_oc_avg
    cj.loc[np.isnan(cj.precip_mm), 'precip_mm'] = cj.precip_mm_avg
    cj.loc[np.isnan(cj.srad_wm2), 'srad_wm2'] = cj.srad_wm2_avg
    cj.loc[np.isnan(cj.vapo_kpa), 'vapo_kpa'] = cj.vapo_kpa_avg


## CHECK FOR OUTLIERS
cjstd = cj.dropna().groupby(['lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].std()
cjstd.rename(columns={'tas_oc': 'tas_oc_std', 'vapo_kpa': 'vapo_kpa_std', 'precip_mm': 'precip_mm_std', 'srad_wm2':'srad_wm2_std'}, inplace=True)
cj = pd.merge(cj, cjstd, how='outer', on=['lat','lon','month'])
cj.loc[(cj.tas_oc > cj.tas_oc_avg + 5 * cj.tas_oc_std), 'tas_oc'] = cj.tas_oc_avg
cj.loc[(cj.tas_oc < cj.tas_oc_avg - 5 * cj.tas_oc_std), 'tas_oc'] = cj.tas_oc_avg
cj.loc[(cj.precip_mm > cj.precip_mm_avg + 5 * cj.precip_mm_std), 'precip_mm'] = cj.precip_mm_avg
cj.loc[(cj.precip_mm < cj.precip_mm_avg - 5 * cj.precip_mm_std), 'precip_mm'] = cj.precip_mm_avg
cj.loc[(cj.srad_wm2 > cj.srad_wm2_avg + 5 * cj.srad_wm2_std), 'srad_wm2'] = cj.srad_wm2_avg
cj.loc[(cj.srad_wm2 < cj.srad_wm2_avg - 5 * cj.srad_wm2_std), 'srad_wm2'] = cj.srad_wm2_avg
cj.loc[(cj.vapo_kpa > cj.vapo_kpa_avg + 5 * cj.vapo_kpa_std), 'vapo_kpa'] = cj.vapo_kpa_avg
cj.loc[(cj.vapo_kpa < cj.vapo_kpa_avg - 5 * cj.vapo_kpa_std), 'vapo_kpa'] = cj.vapo_kpa_avg
cj = cj[['lat','lon','time','month','tas_oc','precip_mm','srad_wm2','vapo_kpa']]

if cj[cj['srad_wm2'] < 0].shape[0] > 0:
    print('Negative radiation values!')
    if cj[cj['srad_wm2']<0]['srad_wm2'].min() < -0.5:
        print('NEGATIVE VALUES OF RADIATION < -0.5!')
    else:
        cj['srad_wm2'] = np.where(cj['srad_wm2'] < 0, 0, cj['srad_wm2'])

if cj[cj['precip_mm'] < 0].shape[0] > 0:
    print('Negative precipitation values!')
    if cj[cj['precip_mm']<0]['precip_mm'].min() < -0.5:
        print('NEGATIVE VALUES OF PRECIPITATION < -0.5!')
    else:
        cj['precip_mm'] = np.where(cj['precip_mm'] < 0, 0, cj['precip_mm'])

if cj[cj['vapo_kpa'] < 0].shape[0] > 0:
    print('Negative pressure values!')
    if cj[cj['vapo_kpa']<0]['vapo_kpa'].min() < -0.1:
        print('NEGATIVE VALUES OF VAPOR PRESSURE < -0.1!')
    else:
        cj['vapo_kpa'] = np.where(cj['vapo_kpa'] < 0, 0, cj['vapo_kpa'])

if cj[(cj['tas_oc'] < -100) | (cj['tas_oc'] > 50)].shape[0] > 0:
    print('Absolute temperature values too high!')
    cj[(cj['tas_oc'] < -100) | (cj['tas_oc'] > 50)]

cjnc = cj.set_index(['time', 'lat', 'lon']).to_xarray()
cjnc.to_netcdf(os.path.join(out_path,'climate_downscaling/CRU_JRA','cj_gf.nc'),unlimited_dims='time')
del [cj, cjmean, cjstd, cjnc]
gc.collect()




### ERA5 

## READ DATA
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/ERA5','era5_unit.nc'))
era5 = ddo.to_dataframe()
era5.reset_index(inplace=True)

## CHECK FOR GAPS
era5check = era5.sort_values(['lat', 'lon','time'])
era5check['deltas'] = era5check['time'].diff()[1:].dt.days
era5check[era5check['deltas'] > 31].shape[0]
if era5check[era5check['deltas'] > 31].shape[0] > 0:
    print('ERA5 number of gaps: ' + era5check[era5check['deltas'] > 31].shape[0])
    ds = pd.date_range(start='1940-01-01', end='2024-12-01', freq='MS')
    lats = era5[['lat']].drop_duplicates()
    lons = era5[['lon']].drop_duplicates()
    da = xr.DataArray(np.arange(len(ds)*len(lats)*len(lons)).reshape(len(ds), len(lats), len(lons)), [("time", ds),("lat", lats['lat']), ("lon", lons['lon'])]).rename("my_data").to_dataframe()
    da.reset_index(inplace=True)
    era5 = pd.merge(era5,da,how='outer',on=['time','lat','lon'])

## CHECK FOR MISSING VALUES 
era5mean = era5.dropna().groupby(['lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].mean()
era5mean.reset_index(inplace=True)
era5mean.rename(columns={'tas_oc': 'tas_oc_avg', 'vapo_kpa': 'vapo_kpa_avg', 'precip_mm': 'precip_mm_avg', 'srad_wm2':'srad_wm2_avg'}, inplace=True)
era5 = pd.merge(era5, era5mean, how='outer', on=['lat','lon','month'])
if (len(era5[np.isnan(era5['tas_oc'])]) > 0)| (len(era5[np.isnan(era5['precip_mm'])]) > 0) | (len(era5[np.isnan(era5['srad_wm2'])]) > 0) | (len(era5[np.isnan(era5['vapo_kpa'])]) > 0):
    era5.loc[np.isnan(era5.tas_oc), 'tas_oc'] = era5.tas_oc_avg
    era5.loc[np.isnan(era5.precip_mm), 'precip_mm'] = era5.precip_mm_avg
    era5.loc[np.isnan(era5.srad_wm2), 'srad_wm2'] = era5.srad_wm2_avg
    era5.loc[np.isnan(era5.vapo_kpa), 'vapo_kpa'] = era5.vapo_kpa_avg

## CHECK FOR OUTLIERS
era5std = era5.dropna().groupby(['lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].std()
era5std.reset_index(inplace=True)
era5std.rename(columns={'tas_oc': 'tas_oc_std', 'vapo_kpa': 'vapo_kpa_std', 'precip_mm': 'precip_mm_std', 'srad_wm2':'srad_wm2_std'}, inplace=True)
era5 = pd.merge(era5, era5std, how='outer', on=['lat','lon','month'])
era5.loc[(era5.tas_oc > era5.tas_oc_avg + 5 * era5.tas_oc_std), 'tas_oc'] = era5.tas_oc_avg
era5.loc[(era5.tas_oc < era5.tas_oc_avg - 5 * era5.tas_oc_std), 'tas_oc'] = era5.tas_oc_avg
era5.loc[(era5.precip_mm > era5.precip_mm_avg + 5 * era5.precip_mm_std), 'precip_mm'] = era5.precip_mm_avg
era5.loc[(era5.precip_mm < era5.precip_mm_avg - 5 * era5.precip_mm_std), 'precip_mm'] = era5.precip_mm_avg
era5.loc[(era5.srad_wm2 > era5.srad_wm2_avg + 5 * era5.srad_wm2_std), 'srad_wm2'] = era5.srad_wm2_avg
era5.loc[(era5.srad_wm2 < era5.srad_wm2_avg - 5 * era5.srad_wm2_std), 'srad_wm2'] = era5.srad_wm2_avg
era5.loc[(era5.vapo_kpa > era5.vapo_kpa_avg + 5 * era5.vapo_kpa_std), 'vapo_kpa'] = era5.vapo_kpa_avg
era5.loc[(era5.vapo_kpa < era5.vapo_kpa_avg - 5 * era5.vapo_kpa_std), 'vapo_kpa'] = era5.vapo_kpa_avg
era5 = era5[['lat','lon','time','month','tas_oc','precip_mm','srad_wm2','vapo_kpa']]

if era5[era5['srad_wm2'] < 0].shape[0] > 0:
    print('Negative radiation values!')
    if era5[era5['srad_wm2']<0]['srad_wm2'].min() < -0.5:
        print('NEGATIVE VALUES OF RADIATION < -0.5!')
    else:
        era5['srad_wm2'] = np.where(era5['srad_wm2'] < 0, 0, era5['srad_wm2'])

if era5[era5['precip_mm'] < 0].shape[0] > 0:
    print('Negative precipitation values!')
    if era5[era5['precip_mm']<0]['precip_mm'].min() < -0.5:
        print('NEGATIVE VALUES OF PRECIPITATION < -0.5!')
    else:
        era5['precip_mm'] = np.where(era5['precip_mm'] < 0, 0, era5['precip_mm'])

if era5[era5['vapo_kpa'] < 0].shape[0] > 0:
    print('Negative pressure values!')
    if era5[era5['vapo_kpa']<0]['vapo_kpa'].min() < -0.1:
        print('NEGATIVE VALUES OF VAPOR PRESSURE < -0.1!')
    else:
        era5['vapo_kpa'] = np.where(era5['vapo_kpa'] < 0, 0, era5['vapo_kpa'])

if era5[(era5['tas_oc'] < -100) | (era5['tas_oc'] > 50)].shape[0] > 0:
    print('Absolute temperature values too high!')
    era5[(era5['tas_oc'] < -100) | (era5['tas_oc'] > 50)]

era5nc = era5.set_index(['time', 'lat', 'lon']).to_xarray()
era5nc.to_netcdf(os.path.join(out_path,'climate_downscaling/ERA5','era5_gf.nc'),unlimited_dims='time')
del [era5, era5mean, era5std]
gc.collect()



### CMIP

## READ DATA
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CMIP','cmip_unit.nc'))
cmip = ddo.to_dataframe()
cmip.reset_index(inplace=True)

## CHECK FOR GAPS
cmipcheck = cmip.sort_values(['scenario','model','lat', 'lon','time'])
cmipcheck['deltas'] = cmipcheck['time'].diff()[1:].dt.days
cmipcheck[cmipcheck['deltas'] > 31].shape[0]
if cmipcheck[cmipcheck['deltas'] > 31].shape[0] > 0:
    print('CMIP number of gaps: ' + str(cmipcheck[cmipcheck['deltas'] > 31].shape[0]))
    ds = pd.date_range(start='2015-01-01', end='2100-12-01', freq='MS')
    lats = cmip[['lat']].drop_duplicates()
    lons = cmip[['lon']].drop_duplicates()
    da = xr.DataArray(np.arange(len(ds)*len(lats)*len(lons)).reshape(len(ds), len(lats), len(lons)), [("time", ds),("lat", lats['lat']), ("lon", lons['lon'])]).rename("my_data").to_dataframe()
    da.reset_index(inplace=True)
    cmip = pd.merge(cmip,da,how='outer',on=['time','lat','lon'])

del [cmipcheck]
gc.collect()

## CHECK FOR MISSING VALUES 
cmipmean = cmip.dropna().groupby(['scenario','model','lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].mean()
cmipmean.reset_index(inplace=True)
cmipmean.rename(columns={'tas_oc': 'tas_oc_avg', 'vapo_kpa': 'vapo_kpa_avg', 'precip_mm': 'precip_mm_avg', 'srad_wm2':'srad_wm2_avg'}, inplace=True)
cmip = pd.merge(cmip, cmipmean, how='outer', on=['scenario','model','lat','lon','month'])
if (len(cmip[np.isnan(cmip['tas_oc'])]) > 0)| (len(cmip[np.isnan(cmip['precip_mm'])]) > 0) | (len(cmip[np.isnan(cmip['srad_wm2'])]) > 0) | (len(cmip[np.isnan(cmip['vapo_kpa'])]) > 0):
    cmip.loc[np.isnan(cmip.tas_oc), 'tas_oc'] = cmip.tas_oc_avg
    cmip.loc[np.isnan(cmip.precip_mm), 'precip_mm'] = cmip.precip_mm_avg
    cmip.loc[np.isnan(cmip.srad_wm2), 'srad_wm2'] = cmip.srad_wm2_avg
    cmip.loc[np.isnan(cmip.vapo_kpa), 'vapo_kpa'] = cmip.vapo_kpa_avg

del [cmipmean]
gc.collect()

## CHECK FOR OUTLIERS
cmipstd = cmip.dropna().groupby(['scenario','model','lat','lon','month'])[['tas_oc','precip_mm','srad_wm2','vapo_kpa']].std()
cmipstd.reset_index(inplace=True)
cmipstd.rename(columns={'tas_oc': 'tas_oc_std', 'vapo_kpa': 'vapo_kpa_std', 'precip_mm': 'precip_mm_std', 'srad_wm2':'srad_wm2_std'}, inplace=True)
cmip = pd.merge(cmip, cmipstd, how='outer', on=['scenario','model','lat','lon','month'])
cmip.loc[(cmip.tas_oc > cmip.tas_oc_avg + 5 * cmip.tas_oc_std), 'tas_oc'] = cmip.tas_oc_avg
cmip.loc[(cmip.tas_oc < cmip.tas_oc_avg - 5 * cmip.tas_oc_std), 'tas_oc'] = cmip.tas_oc_avg
cmip.loc[(cmip.precip_mm > cmip.precip_mm_avg + 5 * cmip.precip_mm_std), 'precip_mm'] = cmip.precip_mm_avg
cmip.loc[(cmip.precip_mm < cmip.precip_mm_avg - 5 * cmip.precip_mm_std), 'precip_mm'] = cmip.precip_mm_avg
cmip.loc[(cmip.srad_wm2 > cmip.srad_wm2_avg + 5 * cmip.srad_wm2_std), 'srad_wm2'] = cmip.srad_wm2_avg
cmip.loc[(cmip.srad_wm2 < cmip.srad_wm2_avg - 5 * cmip.srad_wm2_std), 'srad_wm2'] = cmip.srad_wm2_avg
cmip.loc[(cmip.vapo_kpa > cmip.vapo_kpa_avg + 5 * cmip.vapo_kpa_std), 'vapo_kpa'] = cmip.vapo_kpa_avg
cmip.loc[(cmip.vapo_kpa < cmip.vapo_kpa_avg - 5 * cmip.vapo_kpa_std), 'vapo_kpa'] = cmip.vapo_kpa_avg
cmip = cmip[['scenario','model','lat','lon','time','tas_oc','precip_mm','srad_wm2','vapo_kpa']]

if cmip[cmip['srad_wm2'] < 0].shape[0] > 0:
    print('Negative radiation values!')
    if cmip[cmip['srad_wm2']<0]['srad_wm2'].min() < -0.5:
        print('NEGATIVE VALUES OF RADIATION < -0.5!')
    else:
        cmip['srad_wm2'] = np.where(cmip['srad_wm2'] < 0, 0, cmip['srad_wm2'])

if cmip[cmip['precip_mm'] < 0].shape[0] > 0:
    print('Negative precipitation values!')
    if cmip[cmip['precip_mm']<0]['precip_mm'].min() < -0.5:
        print('NEGATIVE VALUES OF PRECIPITATION < -0.5!')
    else:
        cmip['precip_mm'] = np.where(cmip['precip_mm'] < 0, 0, cmip['precip_mm'])

if cmip[cmip['vapo_kpa'] < 0].shape[0] > 0:
    print('Negative pressure values!')
    if cmip[cmip['vapo_kpa']<0]['vapo_kpa'].min() < -0.1:
        print('NEGATIVE VALUES OF VAPOR PRESSURE < -0.1!')
    else:
        cmip['vapo_kpa'] = np.where(cmip['vapo_kpa'] < 0, 0, cmip['vapo_kpa'])

if cmip[(cmip['tas_oc'] < -100) | (cmip['tas_oc'] > 50)].shape[0] > 0:
    print('Absolute temperature values too high!')
    cmip[(cmip['tas_oc'] < -100) | (cmip['tas_oc'] > 50)]

cmipnc = cmip.set_index(['scenario','model','time','lat','lon']).to_xarray()
cmipnc.to_netcdf(os.path.join(out_path,'climate_downscaling/CMIP','cmip_gf.nc'),unlimited_dims='time')
del [cmip, cmipstd]
gc.collect()




