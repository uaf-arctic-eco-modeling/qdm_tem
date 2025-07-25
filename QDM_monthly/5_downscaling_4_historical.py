import os
import xarray as xr
import pandas as pd
import numpy as np
from cmethods import adjust


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





### READ DATA

## Era5
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/ERA5','era5_corr.nc'))
era5 = ddo.to_dataframe()
era5.reset_index(inplace=True)

## Cru-jra
ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CRU_JRA','cj_gf.nc'))
cj = ddo.to_dataframe()
cj.reset_index(inplace=True)



### DOWNSCALING CRU-JRA with ERA5

ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/ERA5','era5_corr.nc'))
obsh = ddo.sel(time=slice('1940-01-01', '2023-12-31'))
era5 = ddo.sel(time=slice('1940-01-01', '2024-12-31')).to_dataframe()
era5.reset_index(inplace=True)

ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CRU_JRA','cj_gf.nc'))
if ddo.indexes['time'].day[0] == 2:
    ddo["time"] = ddo["time"] - pd.Timedelta(days=1)

simh = ddo.sel(time=slice('1940-01-01', '2023-12-31'))
simp = ddo.sel(time=slice('1901-01-01', '1939-12-31'))

tas_result = adjust(
    method="quantile_delta_mapping",
    obs=obsh['tas_oc'],
    simh=simh['tas_oc'],
    simp=simp['tas_oc'],
    kind="+",
    n_quantiles = 1000)
tas_all = tas_result.to_dataframe()
tas_all.reset_index(inplace=True)

precip_result = adjust(
    method="quantile_delta_mapping",
    obs=obsh['precip_mm'],
    simh=simh['precip_mm'],
    simp=simp['precip_mm'],
    kind="+",
    n_quantiles = 1000)
precip_all = precip_result.to_dataframe()
precip_all.reset_index(inplace=True)

srad_result = adjust(
    method="quantile_delta_mapping",
    obs=obsh['srad_wm2'],
    simh=simh['srad_wm2'],
    simp=simp['srad_wm2'],
    kind="+",
    n_quantiles = 1000)
srad_all = srad_result.to_dataframe()
srad_all.reset_index(inplace=True)

vapo_result = adjust(
    method="quantile_delta_mapping",
    obs=obsh['vapo_kpa'],
    simh=simh['vapo_kpa'],
    simp=simp['vapo_kpa'],
    kind="+",
    n_quantiles = 1000)
vapo_all = vapo_result.to_dataframe()
vapo_all.reset_index(inplace=True)

cjall = pd.merge(tas_all,precip_all,how='outer',on=['time','lat','lon'])
cjall = pd.merge(cjall,srad_all,how='outer',on=['time','lat','lon'])
cjall = pd.merge(cjall,vapo_all,how='outer',on=['time','lat','lon'])

historical = pd.concat([cjall, era5],axis=0)
historical['vapo_hpa'] = 10*historical['vapo_kpa']
historical['year'] = historical['time'].dt.year
historical['month'] = historical['time'].dt.month
historical = pd.merge(historical,month_info,how='outer',on='month')
historical['ddays'] = ((historical['year']-1901)*365) - 1 + historical['doy_noleap']
historical = historical[['ddays','lat','lon','tas_oc', 'precip_mm', 'srad_wm2', 'vapo_hpa']]
historical = historical.rename(columns={'ddays':'time','vapo_hpa': 'vapor_press', 'tas_oc': 'tair', 'srad_wm2': 'nirr', 'precip_mm': 'precip', 'lat': 'Y', 'lon': 'X'})
historical = historical.sort_values(by=['time','Y','X'])
historical.reset_index(inplace=True)

tmp = historical.set_index(['time', 'Y', 'X']).to_xarray()
mask_nc = xr.open_dataset(mask_path)
historical_nc = xr.merge([tmp, mask_nc])
historical_nc = historical_nc.drop_vars(['run','index'])
historical_nc['lat'] = historical_nc['lat'].astype(np.single)
historical_nc['lon'] = historical_nc['lon'].astype(np.single)
historical_nc['time'] = historical_nc['time'].astype(np.double)
historical_nc['tair'] = historical_nc['tair'].astype(np.single)
historical_nc['precip'] = historical_nc['precip'].astype(np.single)
historical_nc['nirr'] = historical_nc['nirr'].astype(np.single)
historical_nc['vapor_press'] = historical_nc['vapor_press'].astype(np.single)
historical_nc['lat'].attrs={'standard_name':'latitude','units':'degree_north'}
historical_nc['lon'].attrs={'standard_name':'longitude','units':'degree_east'}
historical_nc['tair'].attrs={'standard_name':'air_temperature','units':'celsius','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
historical_nc['precip'].attrs={'standard_name':'precipitation_amount','units':'mm month-1','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
historical_nc['nirr'].attrs={'standard_name':'downwelling_shortwave_flux_in_air','units':'W m-2','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
historical_nc['vapor_press'].attrs={'standard_name':'water_vapor_pressure','units':'hPa','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
historical_nc['time'].attrs={'units':'days since 1901-1-1 0:0:0','long_name':'time','calendar':'365_day'}
historical_nc.time.encoding['units'] = 'days since 1901-01-01 00:00:00'
historical_nc.time.encoding['calendar'] = '365_day'
historical_nc.time.encoding['long_name'] = 'time'
#historical_nc = historical_nc.sel(time=slice('1901-01-01', '2024-12-31'))
historical_nc.to_netcdf(os.path.join(out_path,'input/historic-climate.nc'),unlimited_dims='time')

#verif = xr.open_dataset(os.path.join(out_path,'input/historic-climate.nc'))
#verif


