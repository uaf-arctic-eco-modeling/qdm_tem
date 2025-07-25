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

mask_nc = xr.open_dataset(mask_path)

ddo = xr.open_dataset(os.path.join(out_path,'climate_downscaling/ERA5','era5_corr.nc'))
obsh = ddo.sel(time=slice('1970-01-01', '2024-12-01'))

cmiph = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CMIP','cmip_hist_unit.nc'))
cmip = xr.open_dataset(os.path.join(out_path,'climate_downscaling/CMIP','cmip_gf.nc'))



### DOWNSCALING CMIP with ERA5

for mod in modlist:
    print(mod)
    ddo1 = cmiph.sel(model=mod)
    ddo2 = cmip.sel(model=mod, time=slice('2015-01-01', '2024-12-01'))
    ddo2 = ddo2.mean(dim=['scenario'])
    simh = xr.concat([ddo1,ddo2], dim='time')
    simh = simh.sel(time=slice('1970-01-01', '2024-12-01'))
    for sc in sclist:
        print(sc)
        simp = cmip.sel(model=mod, scenario=sc,time=slice('2024-01-01', '2100-12-31'))
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
        result = xr.merge([tas_result,precip_result,srad_result,vapo_result])
        result['vapo_hpa'] = 10*result['vapo_kpa']
        result = result.drop_vars('vapo_kpa')
        result = result.drop(['model','scenario'])
        result = result.rename(lat='Y', lon='X', tas_oc='tair', precip_mm='precip', srad_wm2='nirr', vapo_hpa='vapor_press')
        future = result.to_dataframe()
        future.reset_index(inplace=True)
        future['year'] = future['time'].dt.year
        future['month'] = future['time'].dt.month
        future = future[future['year']>2024]
        future = pd.merge(future,month_info,how='outer',on='month')
        future['ddays'] = ((future['year']-1901)*365) - 1 + future['doy_noleap']
        future = future[['ddays','X','Y','tair', 'precip', 'nirr', 'vapor_press']]
        #future = future[['ddays','X','Y','lat','lon','tair', 'precip', 'nirr', 'vapor_press']]
        future = future.rename(columns={'ddays':'time'})
        future = future.sort_values(by=['time','Y','X'])
        future.reset_index(inplace=True)
        result = future.set_index(['time', 'Y', 'X']).to_xarray()
        result = result.drop_vars(['index'])
        result = xr.merge([result, mask_nc])
        result = result.drop_vars(['run'])
        result['lat'] = result['lat'].astype(np.single)
        result['lon'] = result['lon'].astype(np.single)
        result['time'] = result['time'].astype(np.double)
        result['tair'] = result['tair'].astype(np.single)
        result['precip'] = result['precip'].astype(np.single)
        result['nirr'] = result['nirr'].astype(np.single)
        result['vapor_press'] = result['vapor_press'].astype(np.single)
        result['lat'].attrs={'standard_name':'latitude','units':'degree_north','_FillValue': -999.0}
        result['lon'].attrs={'standard_name':'longitude','units':'degree_east','_FillValue': -999.0}
        result['tair'].attrs={'standard_name':'air_temperature','units':'celsius','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
        result['precip'].attrs={'standard_name':'precipitation_amount','units':'mm month-1','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
        result['nirr'].attrs={'standard_name':'downwelling_shortwave_flux_in_air','units':'W m-2','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
        result['vapor_press'].attrs={'standard_name':'water_vapor_pressure','units':'hPa','grid_mapping':'albers_conical_equal_area','_FillValue': -999.0}
        result['time'].attrs={'units':'days since 1901-1-1 0:0:0','long_name':'time','calendar':'365_day'}
        result.time.encoding['units'] = 'days since 1901-01-01 00:00:00'
        result.time.encoding['calendar'] = '365_day'
        result.time.encoding['long_name'] = 'time'
        result.to_netcdf(os.path.join(out_path,'input/projected-climate_' + sc + '_' + mod + '.nc'),unlimited_dims='time')

