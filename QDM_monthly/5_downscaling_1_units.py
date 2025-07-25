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


### Monthly information
month = list(range(1, 13, 1))
monthlength=[31,28,31,30,31,30,31,31,30,31,30,31]
first_day_of_month_noleap=[1,32,60,91,121,152,182,213,244,274,305,335]
first_day_of_month_leap=[1,33,61,92,122,153,183,214,245,275,306,336]
#data = {'month': month, 'doy_noleap': first_day_of_month_noleap, 'doy_leap': first_day_of_month_leap, 'length': monthlength}
data = {'month': month, 'doy_noleap': first_day_of_month_noleap, 'length': monthlength}
month_info = pd.DataFrame(data)



### READING GENERAL DATA

## Mask
ddo = xr.open_dataset(mask_path)
mask = ddo.to_dataframe()
mask.reset_index(inplace=True)

## Elevation
ddo = xr.open_dataset(topo_path)
topo = ddo.to_dataframe()
topo.reset_index(inplace=True)
topo = topo[['X','Y','elevation']]
topo = topo.rename(columns={'X': 'lon', 'Y': 'lat'})



### UNIT CONVERSION

## Worldclim

# reading data
ddo = xr.open_dataset(wc_path)
wc = ddo.to_dataframe()
wc.reset_index(inplace=True)
wc['doy_noleap'] = wc['time'].astype(int)
wc = pd.merge(wc,month_info, how='outer', on='doy_noleap')

## WC dataset: https://www.worldclim.org/data/worldclim21.html
wc['srad'] = (1000 * wc['srad']) / (24 * 60 * 60)
wc.rename(columns={'tavg': 'tas_oc', 'prec': 'precip_mm', 'srad':'srad_wm2', 'vapr':'vapo_kpa'}, inplace=True)
wc = wc.drop(['lambert_azimuthal_equal_area','length'], axis=1)
wcnc = wc.set_index(['time', 'lat', 'lon']).to_xarray()
wcnc.to_netcdf(os.path.join(out_path,'climate_downscaling/WORLD_CLIM','wc_unit.nc'),unlimited_dims='time')

del [wc, wcnc]
gc.collect()


## ERA5 

# reading data
ddo = xr.open_dataset(era5_path)
dateidx = ddo.indexes["time"].to_datetimeindex()
ddo['time'] = dateidx
era5 = ddo.to_dataframe()
era5.reset_index(inplace=True)
era5['year'] = era5['time'].dt.year
era5['month'] = era5['time'].dt.month
era5 = pd.merge(era5,month_info, how='outer', on='month')


# ERA5 dataset: https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation
era5['t2m'] -= 273.15
era5['d2m'] -= 273.15
era5['tp'] = era5['tp'] * 1000 * era5['length']
era5['ssrd'] = era5['ssrd'] / (24 * 60 * 60)
era5['vapo_kpa'] = 0.1 * 6.1078 * 10 ** ((era5['d2m'] * 7.5)/(era5['d2m'] + 237.3))
era5.rename(columns={'t2m': 'tas_oc', 'tp': 'precip_mm', 'ssrd':'srad_wm2'}, inplace=True)
era5 = era5.drop(['d2m','length'], axis=1)
era5nc = era5.set_index(['time', 'lat', 'lon']).to_xarray()
era5nc.to_netcdf(os.path.join(out_path,'climate_downscaling/ERA5','era5_unit.nc'),unlimited_dims='time')

del [era5, era5nc]
gc.collect()


## TERRA climate

# reading data
ddo = xr.open_dataset(terra_path)
dateidx = ddo.indexes["time"].to_datetimeindex()
ddo['time'] = dateidx
terra = ddo.to_dataframe()
terra.reset_index(inplace=True)
terra['year'] = terra['time'].dt.year
terra['month'] = terra['time'].dt.month
terra = pd.merge(terra,month_info, how='outer', on='month')

# TERRAclimate dataset: https://www.climatologylab.org/terraclimate-variables.html
terra['tas_oc'] = (terra['tmax'] + terra['tmin']) / (2)
terra.rename(columns={'vap': 'vapo_kpa', 'ppt': 'precip_mm', 'srad':'srad_wm2'}, inplace=True)
terranc = terra.set_index(['time', 'lat', 'lon']).to_xarray()
terranc.to_netcdf(os.path.join(out_path,'climate_downscaling/TERRA','terra_unit.nc'),unlimited_dims='time')

del [terra, terranc]
gc.collect()


## CRUJRA 

# reading data
ddo = xr.open_dataset(cj_path)
dateidx = ddo.indexes["time"].to_datetimeindex()
ddo['time'] = dateidx
cj = ddo.to_dataframe()
cj.reset_index(inplace=True)
cj['year'] = cj['time'].dt.year
cj['month'] = cj['time'].dt.month
cj = pd.merge(cj,month_info, how='outer', on='month')
#cj[(cj['year'] == 1980) & (cj['lat'] == 2002000.0) & (cj['lon'] == -1598000.0)]

# CRUJRA dataset: https://dap.ceda.ac.uk/badc/cru/data/cru_jra/cru_jra_2.1/CRUJRA_V2.1_Read_me.txt?download=1
cj['tmp'] -= 273.15
cj['dswrf'] = cj['dswrf'] / (cj['length'] * 24 * 60 * 60)
cj['vapo_kpa'] = (0.001 * cj['pres'] * cj['spfh']) / (0.622 + 0.378 * cj['spfh'])
cj.rename(columns={'tmp': 'tas_oc', 'pre': 'precip_mm', 'dswrf':'srad_wm2'}, inplace=True)
cj = cj.drop(['spfh','pres','length'], axis=1)
cjnc = cj.set_index(['time', 'lat', 'lon']).to_xarray()
cjnc.to_netcdf(os.path.join(out_path,'climate_downscaling/CRU_JRA','cj_unit.nc'),unlimited_dims='time')

del [cj, cjnc]
gc.collect()


## CMIP

# reading data
for sc in sclist:
    print(sc)
    for mod in modlist:
        print(mod)
        ddo = xr.open_dataset(os.path.join(cmip_path,'CMIP' + cmipversion + '_' + sc + '_' + mod + '_rsmpl.nc' ))
        dateidx = ddo.indexes["time"].to_datetimeindex()
        ddo['time'] = dateidx
        data = ddo.to_dataframe()
        data.reset_index(inplace=True)
        data['year'] = data['time'].dt.year
        data['month'] = data['time'].dt.month
        data = pd.merge(data,month_info, how='outer', on='month')
        data['scenario'] = sc
        data['model'] = mod
        if (sc == sclist[0]) & (mod == modlist[0]):
            cmip = data
        else:
            cmip = pd.concat([cmip,data])

cmip = pd.merge(topo,cmip, how='outer', on=['lat','lon'])

# CMIP dataset: https://cds.climate.copernicus.eu/datasets/projections-cmip6?tab=overview
cmip['tas'] -= 273.15
# Summarized CMIP data are already converted to mm.m-2
#cmip[(cmip['lat'] == 2002000.0) & (cmip['lon'] == -1598000.0) & (cmip['year'] == 2015)]
cmip['pres'] = cmip['psl'] * np.exp((-9.80665 * 0.0289644 * cmip['elevation']) / (8.3144598 * (cmip['tas'] + 273.15)))
cmip['vapo_kpa'] = (0.001 * cmip['pres'] * cmip['huss']) / (0.622 + (1-0.622) * cmip['huss'])
cmip.rename(columns={'tas': 'tas_oc', 'pr': 'precip_mm', 'rsds':'srad_wm2'}, inplace=True)
cmip = cmip[['lon', 'lat', 'time', 'tas_oc', 'precip_mm', 'srad_wm2', 'year', 'month', 'doy_noleap', 'scenario', 'model', 'vapo_kpa']]
cmipnc = cmip.set_index(['scenario','model','time', 'lat', 'lon']).to_xarray()
cmipnc.to_netcdf(os.path.join(out_path,'climate_downscaling/CMIP','cmip_unit.nc'),unlimited_dims='time')

del [cmip, cmipnc]
gc.collect()


## CMIP Historical

# reading data
for mod in modlist:
    print(mod)
    ddo = xr.open_dataset(os.path.join(cmip_path,'CMIP' + cmipversion + '_historical_' + mod + '_rsmpl.nc' ))
    dateidx = ddo.indexes["time"].to_datetimeindex()
    ddo['time'] = dateidx
    data = ddo.to_dataframe()
    data.reset_index(inplace=True)
    data['year'] = data['time'].dt.year
    data['month'] = data['time'].dt.month
    data = pd.merge(data,month_info, how='outer', on='month')
    data['model'] = mod
    if mod == modlist[0]:
        cmiphist = data
    else:
        cmiphist = pd.concat([cmiphist,data])

cmiphist = pd.merge(topo,cmiphist, how='outer', on=['lat','lon'])

# CMIP Historical dataset: https://cds.climate.copernicus.eu/datasets/projections-cmip6?tab=overview
cmiphist['tas'] -= 273.15
cmiphist['pr'] *= 60*60*24*cmiphist['length']
#cmiphist[(cmiphist['lat'] == 2002000.0) & (cmiphist['lon'] == -1598000.0) & (cmiphist['year'] == 2015)]
cmiphist['pres'] = cmiphist['psl'] * np.exp((-9.80665 * 0.0289644 * cmiphist['elevation']) / (8.3144598 * (cmiphist['tas'] + 273.15)))
cmiphist['vapo_kpa'] = (0.001 * cmiphist['pres'] * cmiphist['huss']) / (0.622 + (1-0.622) * cmiphist['huss'])
cmiphist.rename(columns={'tas': 'tas_oc', 'pr': 'precip_mm', 'rsds':'srad_wm2'}, inplace=True)
cmiphist = cmiphist.drop(['huss','psl','length','elevation','pres'], axis=1)
cmiphist = cmiphist[['lon', 'lat', 'time', 'tas_oc', 'precip_mm', 'srad_wm2', 'year', 'month', 'doy_noleap', 'model', 'vapo_kpa']]
cmiphistnc = cmiphist.set_index(['model','time', 'lat', 'lon']).to_xarray()
cmiphistnc.to_netcdf(os.path.join(out_path,'climate_downscaling/CMIP','cmip_hist_unit.nc'),unlimited_dims='time')

del [cmiphist, cmiphistnc]
gc.collect()

